from django.db import migrations, models


def asignar_estado_segun_stock(apps, schema_editor):
    Producto = apps.get_model('inventario', 'Producto')
    Producto.objects.filter(stock=0).update(estado='sin_stock')
    Producto.objects.filter(stock__gte=1, stock__lt=10).update(estado='stock_bajo')
    Producto.objects.filter(stock__gte=10).update(estado='disponible')


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_producto_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='estado',
            field=models.CharField(
                choices=[
                    ('disponible', 'Disponible'),
                    ('stock_bajo', 'Stock bajo'),
                    ('sin_stock', 'Sin stock'),
                ],
                default='disponible',
                max_length=20,
                verbose_name='Estado del producto',
            ),
        ),
        migrations.RunPython(asignar_estado_segun_stock, migrations.RunPython.noop),
    ]