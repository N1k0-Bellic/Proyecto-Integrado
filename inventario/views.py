from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib import messages
from .models import Producto
from .forms import ProductoForm

# 1. Listado de Productos
class ProductoListView(ListView):
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        # Permite consultar todos los productos o filtrar solo activos si se especifica
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
            # warning o error suelen pintar el pop-up de amarillo/rojo en CSS
            messages.error(request, f"El producto {producto.nombre} ha sido desactivado.")
            
        return redirect('producto_list')