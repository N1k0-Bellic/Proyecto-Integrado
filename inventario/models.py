from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

UMBRAL_STOCK_BAJO = 10


def _incluir_en_update_fields(kwargs, *campos):
    update_fields = kwargs.get("update_fields")
    if update_fields is not None:
        kwargs["update_fields"] = set(update_fields) | set(campos)


# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la categoría")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la unidad")
    simbolo = models.CharField(max_length=10, verbose_name="Símbolo")

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"


# ---------------------------------------------------------------------------
# Producto y Lote
# ---------------------------------------------------------------------------

class Producto(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        STOCK_BAJO = "stock_bajo", "Stock bajo"
        SIN_STOCK = "sin_stock", "Sin stock"

    codigo = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Código de producto")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del producto")
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="productos", verbose_name="Categoría"
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida, on_delete=models.CASCADE, related_name="productos", verbose_name="Unidad de medida"
    )
    esta_activo = models.BooleanField(default=True, verbose_name="Está activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock actual")
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE, verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def actualizar_estado(self):
        self.esta_activo = self.stock > 0
        if self.stock == 0:
            self.estado = self.Estado.SIN_STOCK
        elif self.stock >= UMBRAL_STOCK_BAJO:
            self.estado = self.Estado.DISPONIBLE
        else:
            self.estado = self.Estado.STOCK_BAJO

    def save(self, *args, **kwargs):
        self.actualizar_estado()
        _incluir_en_update_fields(kwargs, "esta_activo", "estado")
        super().save(*args, **kwargs)


class Lote(models.Model):
    class Estado(models.TextChoices):
        VIGENTE = "vigente", "Vigente"
        VENCIDO = "vencido", "Vencido"
        SIN_VENCIMIENTO = "sin_vencimiento", "Sin vencimiento"

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="lotes", verbose_name="Producto"
    )
    identificador = models.CharField(max_length=50, unique=True, verbose_name="Identificador de lote")
    existencias = models.PositiveIntegerField(verbose_name="Existencias (ud.)")
    fecha_vencimiento = models.DateField(verbose_name="Vencimiento", blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.VIGENTE, verbose_name="Estado del lote"
    )

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ["fecha_vencimiento"]

    def __str__(self):
        return f"Lote de {self.producto.nombre} - Vence el {self.fecha_vencimiento}"

    def actualizar_estado(self):
        if self.fecha_vencimiento is None:
            self.estado = self.Estado.SIN_VENCIMIENTO
        elif timezone.now().date() >= self.fecha_vencimiento:
            self.estado = self.Estado.VENCIDO
        else:
            self.estado = self.Estado.VIGENTE

    def save(self, *args, **kwargs):
        self.actualizar_estado()
        _incluir_en_update_fields(kwargs, "estado")
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Movimientos: Entrada y Salida
# ---------------------------------------------------------------------------

class Entrada(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="entradas")
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="entradas", null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entradas_registradas"
    )
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Entrada #{self.id} - {self.producto.nombre} ({self.cantidad})"

    def clean(self):
        errores = {}
        if not self.lote_id:
            errores["lote"] = "Debe seleccionar un lote."
        elif self.producto_id and self.lote.producto_id != self.producto_id:
            errores["lote"] = "El lote seleccionado no pertenece al producto."
        if self.cantidad is not None and self.cantidad <= 0:
            errores["cantidad"] = "La cantidad debe ser mayor que cero."
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Las entradas no se pueden modificar. Registra una salida para corregir.")
        self.full_clean()
        with transaction.atomic():
            lote = Lote.objects.select_for_update().get(pk=self.lote_id)
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)
            lote.existencias += self.cantidad
            producto.stock += self.cantidad
            lote.save(update_fields=["existencias"])
            producto.save(update_fields=["stock"])
            super().save(*args, **kwargs)


class Salida(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="salidas")
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="salidas", null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="salidas_registradas"
    )
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Salida"
        verbose_name_plural = "Salidas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Salida #{self.id} - {self.producto.nombre} ({self.cantidad})"

    def _validar_stock(self, lote, producto):
        if self.cantidad > lote.existencias:
            raise ValidationError(
                {"cantidad": f"Stock insuficiente en el lote (disponibles: {lote.existencias})."}
            )
        if self.cantidad > producto.stock:
            raise ValidationError(
                {"cantidad": f"Stock insuficiente del producto (disponibles: {producto.stock})."}
            )

    def clean(self):
        errores = {}
        if not self.lote_id:
            errores["lote"] = "Debe seleccionar un lote."
        elif self.producto_id and self.lote.producto_id != self.producto_id:
            errores["lote"] = "El lote seleccionado no pertenece al producto."
        if self.cantidad is not None and self.cantidad <= 0:
            errores["cantidad"] = "La cantidad debe ser mayor que cero."
        if errores:
            raise ValidationError(errores)
        if self.cantidad is not None and self.producto_id:
            self._validar_stock(self.lote, self.producto)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Las salidas no se pueden modificar. Registra una entrada para corregir.")
        self.full_clean()
        with transaction.atomic():
            lote = Lote.objects.select_for_update().get(pk=self.lote_id)
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)
            self._validar_stock(lote, producto)
            lote.existencias -= self.cantidad
            producto.stock -= self.cantidad
            lote.save(update_fields=["existencias"])
            producto.save(update_fields=["stock"])
            super().save(*args, **kwargs)