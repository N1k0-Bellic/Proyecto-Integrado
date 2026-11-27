from django.db import migrations
from django.db.models import Sum


def sincronizar_stock_con_lotes(apps, schema_editor):
    Producto = apps.get_model("inventario", "Producto")
    Lote = apps.get_model("inventario", "Lote")
    base_de_datos = schema_editor.connection.alias

    existencias_por_producto = dict(
        Lote.objects.using(base_de_datos)
        .values("producto_id")
        .annotate(total=Sum("existencias"))
        .values_list("producto_id", "total")
    )

    productos = list(Producto.objects.using(base_de_datos).all())
    for producto in productos:
        producto.stock = existencias_por_producto.get(producto.pk, 0)
        if producto.stock == 0:
            producto.estado = "sin_stock"
        elif producto.stock < 10:
            producto.estado = "stock_bajo"
        else:
            producto.estado = "disponible"

    Producto.objects.using(base_de_datos).bulk_update(productos, ["stock", "estado"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0011_alter_entrada_lote_alter_entrada_producto_and_more"),
    ]

    operations = [
        migrations.RunPython(
            sincronizar_stock_con_lotes,
            migrations.RunPython.noop,
        ),
    ]
