import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0003_producto_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificador', models.CharField(max_length=50, unique=True, verbose_name='Identificador de lote')),
                ('existencias', models.PositiveIntegerField(verbose_name='Existencias (ud.)')),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Vencimiento')),
                ('estado', models.CharField(choices=[('vigente', 'Vigente'), ('vencido', 'Vencido'), ('sin_vencimiento', 'Sin vencimiento')], default='vigente', max_length=20, verbose_name='Estado del lote')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lotes', to='inventario.producto', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Lote',
                'verbose_name_plural': 'Lotes',
                'ordering': ['fecha_vencimiento'],
            },
        ),
    ]