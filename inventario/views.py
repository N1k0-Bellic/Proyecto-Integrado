
from django.shortcuts import render


# Datos temporales para desarrollar y probar HU-002.
# Posteriormente se reemplazarán por consultas a PostgreSQL.
PRODUCTOS_DEMO = [
    {
        "codigo": "P-001",
        "nombre": "Shampoo Hidratante",
        "categoria": "Shampoo",
        "stock_minimo": 10,
        "lotes": [
            {
                "codigo": "L-001",
                "vencimiento": "15/12/2026",
                "unidades": 12,
                "estado": "Vigente",
            },
            {
                "codigo": "L-002",
                "vencimiento": "20/11/2026",
                "unidades": 8,
                "estado": "Vigente",
            },
            {
                "codigo": "L-003",
                "vencimiento": "10/02/2027",
                "unidades": 5,
                "estado": "Vigente",
            },
        ],
    },
    {
        "codigo": "P-002",
        "nombre": "Mascarilla Reparadora",
        "categoria": "Tratamiento",
        "stock_minimo": 10,
        "lotes": [
            {
                "codigo": "L-004",
                "vencimiento": "20/03/2027",
                "unidades": 8,
                "estado": "Vigente",
            },
        ],
    },
    {
        "codigo": "P-003",
        "nombre": "Crema de Peinar",
        "categoria": "Styling",
        "stock_minimo": 5,
        "lotes": [],
    },
    {
        "codigo": "P-004",
        "nombre": "Gel Definidor",
        "categoria": "Styling",
        "stock_minimo": 5,
        "lotes": [
            {
                "codigo": "L-005",
                "vencimiento": "10/04/2027",
                "unidades": 18,
                "estado": "Vigente",
            },
        ],
    },
    {
        "codigo": "P-005",
        "nombre": "Aceite Capilar",
        "categoria": "Tratamiento",
        "stock_minimo": 5,
        "lotes": [
            {
                "codigo": "L-006",
                "vencimiento": "12/06/2027",
                "unidades": 12,
                "estado": "Vigente",
            },
        ],
    },
    {
        "codigo": "P-006",
        "nombre": "Leave In",
        "categoria": "Styling",
        "stock_minimo": 10,
        "lotes": [
            {
                "codigo": "L-007",
                "vencimiento": "18/08/2027",
                "unidades": 6,
                "estado": "Vigente",
            },
        ],
    },
]


def calcular_stock(lotes):
    """Calcula las existencias físicas sumando sus lotes."""
    return sum(lote["unidades"] for lote in lotes)


def determinar_estado(stock, stock_minimo):
    """Clasifica el estado del stock de un producto."""
    if stock == 0:
        return "Sin stock"

    if stock <= stock_minimo:
        return "Stock bajo"

    return "Disponible"


def consultar_inventario(request):
    busqueda = request.GET.get("buscar", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    codigo = request.GET.get("producto", "").strip()

    productos = []

    # Preparar los datos calculados sin modificar los originales.
    for producto in PRODUCTOS_DEMO:
        stock = calcular_stock(producto["lotes"])

        productos.append({
            **producto,
            "stock": stock,
            "estado": determinar_estado(
                stock,
                producto["stock_minimo"],
            ),
        })

    categorias = sorted({
        producto["categoria"] for producto in productos
    })

    # Buscar por código o nombre.
    if busqueda:
        productos = [
            producto for producto in productos
            if busqueda.lower() in producto["codigo"].lower()
            or busqueda.lower() in producto["nombre"].lower()
        ]

    # Filtrar por categoría.
    if categoria:
        productos = [
            producto for producto in productos
            if producto["categoria"] == categoria
        ]

    # Obtener el producto seleccionado.
    seleccionado = next(
        (
            producto for producto in productos
            if producto["codigo"] == codigo
        ),
        None,
    )

    # Seleccionar el primero cuando no haya selección válida.
    if seleccionado is None and productos:
        seleccionado = productos[0]

    return render(
        request,
        "inventario/consulta.html",
        {
            "productos": productos,
            "seleccionado": seleccionado,
            "categorias": categorias,
            "busqueda": busqueda,
            "categoria_actual": categoria,
        },
    )
