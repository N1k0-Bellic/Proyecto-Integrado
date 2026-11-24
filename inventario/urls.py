from django.urls import path
from . import views
from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDesactivarView,
)

urlpatterns = [
    path('', views.inicio_view, name='home'),
    path('inicio/', views.inicio_view, name='inicio'),
    path('productos/', ProductoListView.as_view(), name='producto_list'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto_create'),
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/<int:pk>/desactivar/', ProductoDesactivarView.as_view(), name='producto_desactivar'),
    path('movimientos/', views.movimientos_view, name='movimientos'),
]