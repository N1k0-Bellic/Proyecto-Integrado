
from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Categoria, Lote, Producto, UnidadMedida

from .servicios_vencimientos import clasificar_vencimiento


class VencimientoTests(SimpleTestCase):

    def setUp(self):
        self.hoy = date(2026, 11, 25)

    def test_lote_vencido(self):
        resultado = clasificar_vencimiento(
            self.hoy - timedelta(days=1),
            self.hoy,
        )
        self.assertEqual(resultado["estado"], "Vencido")

    def test_vence_hoy(self):
        resultado = clasificar_vencimiento(
            self.hoy,
            self.hoy,
        )
        self.assertEqual(resultado["estado"], "Vence hoy")

    def test_proximo_a_vencer(self):
        resultado = clasificar_vencimiento(
            self.hoy + timedelta(days=15),
            self.hoy,
        )
        self.assertEqual(
            resultado["estado"],
            "Próximo a vencer",
        )

    def test_limite_30_dias(self):
        resultado = clasificar_vencimiento(
            self.hoy + timedelta(days=30),
            self.hoy,
        )
        self.assertEqual(
            resultado["estado"],
            "Próximo a vencer",
        )

    def test_vigente(self):
        resultado = clasificar_vencimiento(
            self.hoy + timedelta(days=45),
            self.hoy,
        )
        self.assertEqual(resultado["estado"], "Vigente")

    def test_sin_fecha(self):
        resultado = clasificar_vencimiento(
            None,
            self.hoy,
        )
        self.assertEqual(resultado["estado"], "Sin fecha")

class AlertasViewTests(TestCase):

    def setUp(self):
        categoria = Categoria.objects.create(nombre="Cuidado")
        unidad = UnidadMedida.objects.create(
            nombre="Unidad",
            simbolo="ud",
        )
        producto = Producto.objects.create(
            codigo="ALT-001",
            nombre="Producto de prueba",
            categoria=categoria,
            unidad_medida=unidad,
            stock=2,
        )
        hoy = timezone.localdate()
        Lote.objects.create(
            producto=producto,
            identificador="ALT-VENCIDO",
            existencias=1,
            fecha_vencimiento=hoy - timedelta(days=1),
        )
        Lote.objects.create(
            producto=producto,
            identificador="ALT-PROXIMO",
            existencias=1,
            fecha_vencimiento=hoy + timedelta(days=10),
        )
        Lote.objects.create(
            producto=producto,
            identificador="ALT-VIGENTE",
            existencias=1,
            fecha_vencimiento=hoy + timedelta(days=45),
        )

    def test_pantalla_muestra_solo_lotes_alertados(self):
        response = self.client.get(reverse("alertas"))

        self.assertEqual(response.status_code, 200)
        alertas = response.context["alertas"]
        identificadores = [alerta["codigo_lote"] for alerta in alertas]
        self.assertIn("ALT-VENCIDO", identificadores)
        self.assertIn("ALT-PROXIMO", identificadores)
        self.assertIn("ALT-VIGENTE", identificadores)
