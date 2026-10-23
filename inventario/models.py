from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la categoría")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la unidad") # Ej: Mililitros, Gramos, Unidades
    simbolo = models.CharField(max_length=10, verbose_name="Símbolo") # Ej: ml, g, uds

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"


class Producto(models.Model):
    codigo = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True, 
        verbose_name="Código de producto"
    )  # Impide códigos duplicados
    
    nombre = models.CharField(max_length=150, verbose_name="Nombre del producto")
    
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, 
        related_name="productos", 
        verbose_name="Categoría"
    )  # Permite asociar la categoría requerida
    
    unidad_medida = models.ForeignKey(
        UnidadMedida, 
        on_delete=models.PROTECT, 
        related_name="productos", 
        verbose_name="Unidad de medida"
    )  # Permite asociar la unidad de medida requerida
    
    esta_activo = models.BooleanField(
        default=True, 
        verbose_name="Está activo"
    )  # Desactivar sin borrar registros ni perder historial de movimientos
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"