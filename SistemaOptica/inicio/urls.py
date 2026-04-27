from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('', views.dashboard, name='dashboard'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('inventario/movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('inventario/movimientos/', views.historial_movimientos, name='historial_movimientos'),
]