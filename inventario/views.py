from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, View
from .forms import ProductoForm, SalidaForm
from .models import Entrada, Lote, Producto, Salida
from .servicios_vencimientos import clasificar_vencimiento


# 0. Panel Principal / Inicio
def inicio_view(request):
    productos_activos = Producto.objects.filter(esta_activo=True).count()
    stock_total = (
        Producto.objects.filter(esta_activo=True).aggregate(total=Sum("stock"))["total"] or 0
    )

    hoy = timezone.localdate()
    limite_alerta = hoy + timedelta(days=30)
    
    # Contamos alertas activas (lotes vencidos, vencen hoy o próximos hasta 30 días con existencias)
    cantidad_alertas = Lote.objects.filter(
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=limite_alerta,
        existencias__gt=0,
    ).count()

    return render(
        request,
        "inicio.html",
        {
            "productos_activos": productos_activos,
            "stock_total": stock_total,
            "cantidad_alertas": cantidad_alertas,
        },
    )


# 1. Listado de Productos
class ProductoListView(ListView):
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Producto.objects.all().select_related('categoria', 'unidad_medida').order_by('nombre')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query)
                | Q(codigo__icontains=query)
                | Q(categoria__nombre__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


# 2. Registro de Productos
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, "Producto registrado exitosamente.")
        return super().form_valid(form)


# 3. Edición de Productos
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado exitosamente.")
        return super().form_valid(form)


# 4. Desactivación de Producto
class ProductoDesactivarView(View):
    def post(self, request, pk, *args, **kwargs):
        producto = get_object_or_404(Producto, pk=pk)
        producto.esta_activo = not producto.esta_activo
        producto.save()

        if producto.esta_activo:
            messages.success(request, f"El producto {producto.nombre} ha sido activado.")
        else:
            messages.error(request, f"El producto {producto.nombre} ha sido desactivado.")

        return redirect('producto_list')


# 5. Gestión de Lotes
def lotes_view(request):
    hoy = timezone.localdate()
    limite_alerta = hoy + timedelta(days=30)
    query = request.GET.get("q", "").strip()

    lotes = Lote.objects.select_related("producto").order_by("fecha_vencimiento", "identificador")
    if query:
        lotes = lotes.filter(
            Q(identificador__icontains=query)
            | Q(producto__nombre__icontains=query)
        )

    return render(
        request,
        "lotes.html",
        {
            "lotes": lotes,
            "hoy": hoy,
            "limite_alerta": limite_alerta,
            "query": query,
        },
    )

# 7. Alertas de Lotes
def alertas_view(request):
    hoy = timezone.localdate()
    limite_alerta = hoy + timedelta(days=30)

    query = request.GET.get("q", "").strip()
    estado_filtro = request.GET.get("estado", "").strip()

    lotes_qs = (
        Lote.objects.select_related("producto", "producto__categoria")
        .filter(fecha_vencimiento__isnull=False)
        .order_by("fecha_vencimiento", "identificador")
    )

    if query:
        lotes_qs = lotes_qs.filter(
            Q(identificador__icontains=query)
            | Q(producto__nombre__icontains=query)
            | Q(producto__codigo__icontains=query)
        )

    mapa_tipo = {
        "Vencido": "vencido",
        "Vence hoy": "hoy",
        "Próximo a vencer": "por_vencer",
        "Vigente": "vigente",
    }

    lotes_alerta = []
    vencidos_count = 0
    vence_hoy_count = 0
    por_vencer_count = 0
    sin_fecha_count = Lote.objects.filter(fecha_vencimiento__isnull=True).count()

    for lote in lotes_qs:
        resultado = clasificar_vencimiento(lote.fecha_vencimiento, hoy)
        dias_restantes = resultado["dias_restantes"]
        tipo = mapa_tipo.get(resultado["estado"], "vigente")

        # Si está próximo a vencer pero no tiene existencias, no lo tratamos como alerta activa
        if tipo == "por_vencer" and lote.existencias <= 0:
            tipo = "vigente"

        lote.dias_restantes = dias_restantes
        lote.dias_vencido = abs(dias_restantes) if dias_restantes is not None else 0
        lote.alerta_tipo = tipo

        if tipo == "vencido":
            vencidos_count += 1
        elif tipo == "hoy":
            vence_hoy_count += 1
        elif tipo == "por_vencer":
            por_vencer_count += 1

        if tipo in ["vencido", "hoy", "por_vencer"]:
            if not estado_filtro or estado_filtro == tipo:
                lotes_alerta.append(lote)

    resumen = {
        "vencidos": vencidos_count,
        "vence_hoy": vence_hoy_count,
        "proximos": por_vencer_count,
        "sin_fecha": sin_fecha_count,
    }

    return render(
        request,
        "alertas.html",
        {
            "lotes": lotes_alerta,
            "hoy": hoy,
            "limite_alerta": limite_alerta,
            "query": query,
            "estado_filtro": estado_filtro,
            "resumen": resumen,
        },
    )


# 6. Registro de Entradas y Salidas (Movimientos)
def _obtener_responsable(request):
    if request.user.is_authenticated:
        return request.user
    User = get_user_model()
    return User.objects.order_by("pk").first()


def movimientos_view(request):
    productos = Producto.objects.order_by("nombre")
    lotes = Lote.objects.select_related("producto").order_by("producto__nombre", "identificador")
    salida_form = SalidaForm()

    if request.method == "POST":
        tipo = request.POST.get("tipo", "entrada")  # "entrada" o "salida"
        responsable = _obtener_responsable(request)

        if responsable is None:
            messages.error(request, "No hay un usuario responsable disponible para registrar el movimiento.")
            return redirect("movimientos")

        if tipo == "salida":
            salida_form = SalidaForm(request.POST)
            if salida_form.is_valid():
                salida = salida_form.save(commit=False)
                salida.responsable = responsable
                try:
                    salida.save()
                except ValidationError as exc:
                    if hasattr(exc, "message_dict"):
                        for campo, msgs in exc.message_dict.items():
                            for msg in msgs:
                                if campo in salida_form.fields:
                                    salida_form.add_error(campo, msg)
                                else:
                                    messages.error(request, msg)
                    else:
                        for msg in exc.messages:
                            messages.error(request, msg)
                else:
                    messages.success(request, f"Salida registrada (-{salida.cantidad}) correctamente.")
                    return redirect("movimientos")
            else:
                messages.error(request, "Revisa los datos del formulario de salida.")
        elif tipo == "entrada":
            producto_id = request.POST.get("producto") or None
            lote_id = request.POST.get("lote") or None
            cantidad_raw = request.POST.get("cantidad", "").strip()
            observaciones = request.POST.get("observaciones", "").strip()

            try:
                cantidad = int(cantidad_raw)
            except (TypeError, ValueError):
                messages.error(request, "Ingresa una cantidad numérica válida.")
                return redirect("movimientos")

            entrada = Entrada(
                producto_id=producto_id,
                lote_id=lote_id,
                cantidad=cantidad,
                responsable=responsable,
                observaciones=observaciones or None,
            )
            try:
                entrada.save()
            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    for msgs in exc.message_dict.values():
                        for msg in msgs:
                            messages.error(request, msg)
                else:
                    for msg in exc.messages:
                        messages.error(request, msg)
                return redirect("movimientos")

            messages.success(request, f"Entrada registrada (+{cantidad}) correctamente.")
            return redirect("movimientos")
        else:
            messages.error(request, "Selecciona un tipo de movimiento válido (entrada o salida).")

    entradas = Entrada.objects.select_related("producto", "lote", "responsable")[:15]
    salidas = Salida.objects.select_related("producto", "lote", "responsable")[:15]

    return render(
        request,
        "movimientos.html",
        {
            "productos": productos,
            "lotes": lotes,
            "entradas": entradas,
            "salidas": salidas,
            "salida_form": salida_form,
        },
    )