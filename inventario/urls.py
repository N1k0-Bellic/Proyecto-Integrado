
from django.urls import path
from . import views

urlpatterns = [
    path("", views.consultar_inventario, name="consultar_inventario"),
]
