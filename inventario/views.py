
from django.shortcuts import render

# Datos temporales para construir la interfaz.
# Después serán reemplazados por consultas a PostgreSQL.
PRODUCTOS_DEMO = [
    {
        "codigo": "P-001",
        "nombre": "Shampoo Hidratante",
        "categoria": "Shampoo",
        "stock": 25,
        "estado": "Disponible",
        "lotes": [
            {"codigo": "L-001", "vencimiento": "15/12/2026", "unidades": 12, "estado": "Vigente"},
            {"codigo": "L-002", "vencimiento": "20/11/2026", "unidades": 8, "estado": "Vigente"},
            {"codigo": "L-003", "vencimiento": "10/02/2027", "unidades": 5, "estado": "Vigente"},
        ],
    },
    {
        "codigo": "P-002",
        "nombre": "Mascarilla Reparadora",
        "categoria": "Tratamiento",
        "stock": 8,
        "estado": "Stock bajo",
        "lotes": [
            {"codigo": "L-004", "vencimiento": "20/03/2027", "unidades": 8, "estado": "Vigente"},
        ],
    },
    {
        "codigo": "P-003",
        "nombre": "Crema de Peinar",
        "categoria": "Styling",
        "stock": 0,
        "estado": "Sin stock",
        "lotes": [],
    },
    {
        "codigo": "P-004",
        "nombre": "Gel Definidor",
        "categoria": "Styling",
        "stock": 18,
        "estado": "Disponible",
        "lotes": [],
    },
    {
        "codigo": "P-005",
        "nombre": "Aceite Capilar",
        "categoria": "Tratamiento",
        "stock": 12,
        "estado": "Disponible",
        "lotes": [],
    },
    {
        "codigo": "P-006",
        "nombre": "Leave In",
        "categoria": "Styling",
        "stock": 6,
        "estado": "Stock bajo",
        "lotes": [],
    },
]


def consultar_inventario(request):
    codigo = request.GET.get("producto", "P-001")

    seleccionado = next(
        (producto for producto in PRODUCTOS_DEMO if producto["codigo"] == codigo),
        None,
    )

    return render(
        request,
        "inventario/consulta.html",
        {
            "productos": PRODUCTOS_DEMO,
            "seleccionado": seleccionado,
        },
    )
