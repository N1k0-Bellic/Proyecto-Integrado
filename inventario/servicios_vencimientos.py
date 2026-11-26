
from django.utils import timezone

from .models import Lote


DIAS_ALERTA = 30


def clasificar_vencimiento(fecha_vencimiento, fecha_actual=None):
    """Clasifica un lote según su fecha de vencimiento."""

    if fecha_actual is None:
        fecha_actual = timezone.localdate()

    if fecha_vencimiento is None:
        return {
            "estado": "Sin fecha",
            "dias_restantes": None,
        }

    dias = (fecha_vencimiento - fecha_actual).days

    if dias < 0:
        estado = "Vencido"
    elif dias == 0:
        estado = "Vence hoy"
    elif dias <= DIAS_ALERTA:
        estado = "Próximo a vencer"
    else:
        estado = "Vigente"

    return {
        "estado": estado,
        "dias_restantes": dias,
    }


def consultar_alertas_vencimiento(fecha_actual=None):
    """
    Consulta lotes reales mediante Django ORM.

    Solo considera lotes con existencias físicas.
    Calcula el estado en cada consulta, sin modificar
    los datos almacenados.
    """

    lotes = (
        Lote.objects
        .select_related("producto")
        .filter(existencias__gt=0)
    )

    alertas = []

    for lote in lotes:
        resultado = clasificar_vencimiento(
            lote.fecha_vencimiento,
            fecha_actual,
        )

        alertas.append({
            "producto": lote.producto.nombre,
            "codigo_producto": lote.producto.codigo,
            "codigo_lote": lote.identificador,
            "fecha_vencimiento": lote.fecha_vencimiento,
            "existencias": lote.existencias,
            "estado": resultado["estado"],
            "dias_restantes": resultado["dias_restantes"],
        })

    prioridad = {
        "Vencido": 0,
        "Vence hoy": 1,
        "Próximo a vencer": 2,
        "Sin fecha": 3,
        "Vigente": 4,
    }

    alertas.sort(
        key=lambda alerta: (
            prioridad[alerta["estado"]],
            alerta["fecha_vencimiento"] or timezone.localdate(),
        )
    )

    return alertas
