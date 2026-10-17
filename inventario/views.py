from django.shortcuts import render

from django.shortcuts import render


def consultar_inventario(request):
    return render(request, "inventario/consulta.html")
