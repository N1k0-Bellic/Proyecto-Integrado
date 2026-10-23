from django import forms
from .models import Producto

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

    # Validación de código duplicado 
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        query = Producto.objects.filter(codigo=codigo)
        
        # Si estamos editando, excluimos el producto actual de la búsqueda
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
            
        if query.exists():
            raise forms.ValidationError("Ya existe un producto registrado con este código.")
            
        return codigo