from django.db import models
from django.utils import timezone

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

    # Cantidad disponible en inventario
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock actual")

    estado = models.CharField(
        max_length=20,
        choices=[
            ('disponible', 'Disponible'),
            ('stock_bajo', 'Stock bajo'),
            ('sin_stock', 'Sin stock')
        ],
        default='disponible',
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        self.esta_activo = self.stock > 0
        if self.stock == 0:
            self.estado = 'sin_stock'
        elif self.stock >= 10:
            self.estado = 'disponible'
        else:
            self.estado = 'stock_bajo'
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"esta_activo", "estado"}
        super().save(*args, **kwargs)

class Lote(models.Model):
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT, 
        related_name="lotes", 
        verbose_name="Producto"
    )
    identificador = models.CharField(max_length=50, unique=True, verbose_name="Identificador de lote")
    existencias = models.PositiveIntegerField(verbose_name="Existencias (ud.)")
    fecha_vencimiento = models.DateField(verbose_name="Vencimiento", blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('vigente', 'Vigente'),
            ('vencido', 'Vencido'),
            ('sin_vencimiento', 'Sin vencimiento'),
        ],
        default='vigente',
        verbose_name="Estado del lote"
    )

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['fecha_vencimiento']

    def __str__(self):
        return f"Lote de {self.producto.nombre} - Vence el {self.fecha_vencimiento}"

    def actualizar_estado(self):
        if self.fecha_vencimiento is None:
            self.estado = 'sin_vencimiento'
        elif timezone.now().date() >= self.fecha_vencimiento:
            self.estado = 'vencido'
        else:
            self.estado = 'vigente'

    def save(self, *args, **kwargs):
        self.actualizar_estado()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"estado"}
        super().save(*args, **kwargs)