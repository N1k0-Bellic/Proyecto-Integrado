from django.contrib import admin
from .models import Categoria, Producto, UnidadMedida

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
        "codigo",
        "nombre",
        "categoria",
        "unidad_medida",
        "esta_activo",
        "fecha_creacion",
        "stock",
    )
    list_filter = ("esta_activo", "categoria", "unidad_medida")
    search_fields = ("codigo", "nombre")
    list_select_related = ("categoria", "unidad_medida")
