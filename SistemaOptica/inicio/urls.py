from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.login, name='login'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('inventario/movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('inventario/movimientos/', views.historial_movimientos, name='historial_movimientos'),
    path('empleados/', views.empleados, name='empleados'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('pacientes/', views.lista_pacientes, name='pacientes'),
    path('pacientes/agregar/', views.agregar_paciente, name='agregar_paciente'),
    path('pacientes/historia/<int:id>/', views.historia_clinica, name='historia_clinica'),
    path('servicios/registrar/', views.registrar_servicio, name='registrar_servicio'),
    path('ventas/', views.lista_ventas, name='ventas'),
    path('ventas/nueva/', views.nueva_venta, name='nueva_venta'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/graficas/', views.reporte_grafica, name='reportes_graficas'),
]
