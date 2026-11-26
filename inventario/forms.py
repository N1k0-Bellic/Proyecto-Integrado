from django import forms
from .models import Lote, Producto, Salida


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'categoria', 'unidad_medida', 'esta_activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. PROD-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
            'esta_activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        query = Producto.objects.filter(codigo=codigo)

        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        if query.exists():
            raise forms.ValidationError("Ya existe un producto registrado con este código.")

        return codigo


class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ['producto', 'lote', 'cantidad', 'observaciones']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select', 'id': 'id_producto'}),
            'lote': forms.Select(attrs={'class': 'form-select', 'id': 'id_lote'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_cantidad', 'min': 1}),
            'observaciones': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'id_observaciones',
                    'placeholder': 'Ej. Venta en salón, consumo interno...',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(esta_activo=True).order_by('nombre')
        self.fields['lote'].queryset = Lote.objects.select_related('producto').order_by('producto__nombre', 'identificador')
        self.fields['producto'].required = True
        self.fields['lote'].required = True
        self.fields['cantidad'].required = True

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError("La cantidad a retirar debe ser mayor que cero.")
        return cantidad

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        lote = cleaned_data.get('lote')
        cantidad = cleaned_data.get('cantidad')

        if producto and lote and lote.producto_id != producto.pk:
            self.add_error('lote', "El lote seleccionado no pertenece al producto elegido.")

        if lote and cantidad is not None and cantidad > lote.existencias:
            self.add_error('cantidad', f"Stock insuficiente en el lote (disponibles: {lote.existencias}).")

        if producto and cantidad is not None and cantidad > producto.stock:
            self.add_error('cantidad', f"Stock insuficiente del producto (disponibles: {producto.stock}).")

        return cleaned_data