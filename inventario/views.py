from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from .models import Producto, Lote, Entrada, Salida
from .forms import ProductoForm


# 1. Listado de Productos
class ProductoListView(ListView):
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        return Producto.objects.all().select_related('categoria', 'unidad_medida')


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


# 5. Registro de Entradas y Salidas (Movimientos)
def _obtener_responsable(request):
    if request.user.is_authenticated:
        return request.user
    User = get_user_model()
    return User.objects.order_by("pk").first()


def movimientos_view(request):
    productos = Producto.objects.order_by("nombre")
    lotes = Lote.objects.select_related("producto").order_by("producto__nombre", "identificador")

    if request.method == "POST":
        tipo = request.POST.get("tipo")  # "entrada" o "salida"
        producto_id = request.POST.get("producto") or None
        lote_id = request.POST.get("lote") or None
        cantidad_raw = request.POST.get("cantidad", "").strip()
        observaciones = request.POST.get("observaciones", "").strip()

        try:
            cantidad = int(cantidad_raw)
        except (TypeError, ValueError):
            messages.error(request, "Ingresa una cantidad numérica válida.")
            return redirect("movimientos")

        responsable = _obtener_responsable(request)
        if responsable is None:
            messages.error(request, "No hay un usuario responsable disponible para registrar el movimiento.")
            return redirect("movimientos")

        if tipo == "entrada":
            movimiento = Entrada(
                producto_id=producto_id,
                lote_id=lote_id,
                cantidad=cantidad,
                responsable=responsable,
                observaciones=observaciones or None,
            )
            exito_msg = f"Entrada registrada (+{cantidad}) correctamente."
        elif tipo == "salida":
            movimiento = Salida(
                producto_id=producto_id,
                lote_id=lote_id,
                cantidad=cantidad,
                responsable=responsable,
                observaciones=observaciones or None,
            )
            exito_msg = f"Salida registrada (-{cantidad}) correctamente."
        else:
            messages.error(request, "Selecciona un tipo de movimiento válido (entrada o salida).")
            return redirect("movimientos")

        try:
            movimiento.save()
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                for msgs in exc.message_dict.values():
                    for msg in msgs:
                        messages.error(request, msg)
            else:
                for msg in exc.messages:
                    messages.error(request, msg)
            return redirect("movimientos")

        messages.success(request, exito_msg)
        return redirect("movimientos")

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
        },
    )