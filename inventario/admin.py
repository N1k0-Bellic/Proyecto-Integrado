from django.contrib import admin

from .models import Categoria, Entrada, Lote, Producto, Salida, UnidadMedida

admin.site.index_title = "Administración de productos"
admin.site.site_header = "Administración de Riza Tus Rizos"
admin.site.site_title = "Riza Tus Rizos"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "simbolo")
    search_fields = ("nombre", "simbolo")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo", "nombre", "categoria", "unidad_medida",
        "esta_activo", "estado", "fecha_creacion", "stock",
    )
    list_filter = ("esta_activo", "categoria", "unidad_medida")
    search_fields = ("codigo", "nombre")
    list_select_related = ("categoria", "unidad_medida")
    readonly_fields = ("estado", "stock")


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("identificador", "producto", "existencias", "fecha_vencimiento", "estado")
    list_filter = ("estado",)
    search_fields = ("identificador", "producto__nombre")
    list_select_related = ("producto",)


class MovimientoAdmin(admin.ModelAdmin):
    """Configuración compartida por Entrada y Salida."""
    list_display = ("id", "producto", "lote", "cantidad", "fecha", "responsable")
    list_filter = ("fecha", "responsable")
    search_fields = ("producto__nombre", "lote__identificador")
    list_select_related = ("producto", "lote", "responsable")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Entrada)
class EntradaAdmin(MovimientoAdmin):
    pass


@admin.register(Salida)
class SalidaAdmin(MovimientoAdmin):
    pass