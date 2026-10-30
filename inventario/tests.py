from django.test import TestCase
from .models import Categoria, Producto, UnidadMedida


class ProductoStockTest(TestCase):
	def setUp(self):
		self.categoria = Categoria.objects.create(nombre="Bebidas")
		self.unidad = UnidadMedida.objects.create(nombre="Unidad", simbolo="ud")

	def crear_producto(self, stock, esta_activo=True):
		return Producto.objects.create(
			codigo="PROD-001",
			nombre="Producto de prueba",
			categoria=self.categoria,
			unidad_medida=self.unidad,
			stock=stock,
			esta_activo=esta_activo,
		)

	def test_stock_cero_desactiva_producto(self):
		producto = self.crear_producto(stock=0)

		self.assertFalse(producto.esta_activo)

	def test_stock_cero_desactiva_producto_al_actualizar_stock(self):
		producto = self.crear_producto(stock=5)
		producto.stock = 0
		producto.save(update_fields=["stock"])

		producto.refresh_from_db()
		self.assertFalse(producto.esta_activo)

	def test_stock_positivo_activa_producto(self):
		producto = self.crear_producto(stock=5, esta_activo=False)

		self.assertTrue(producto.esta_activo)

	def test_stock_positivo_activa_producto_al_actualizar_stock(self):
		producto = self.crear_producto(stock=0)
		producto.stock = 5
		producto.save(update_fields=["stock"])

		producto.refresh_from_db()
		self.assertTrue(producto.esta_activo)
