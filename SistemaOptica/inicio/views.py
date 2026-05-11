import json
from datetime import datetime
from functools import wraps

from django.db import connection, transaction
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    Producto, Categoria, Proveedor, Movimiento, Usuario,
    Paciente, HistoriaClinica, ServicioMedico, Venta,
    DetalleVenta, MovimientoInventario
)

def login_requerido(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def inicio(request):
    return render(request, 'index.html')

@login_requerido
def dashboard(request):
    total_pacientes = Paciente.objects.count()
    productos_criticos = Producto.objects.filter(stock_actual__lte=5).count()

    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy).aggregate(Sum('total_venta'))['total_venta__sum'] or 0

    ultimos_movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha_movimiento')[:5]

    context = {
        'total_pacientes': total_pacientes,
        'productos_criticos': productos_criticos,
        'ventas_hoy': ventas_hoy,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'dashboard.html', context)

@login_requerido
def productos(request):
    productos = Producto.objects.select_related('categoria', 'proveedor').all()
    print(Producto.objects.all())
    print(productos)
    print(request.POST)
    return render(request, 'productos/productos.html', {
        'productos': productos
    })

@login_requerido
def agregar_producto(request):
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':

        categoria = Categoria.objects.get(pk=request.POST.get('categoria_id'))
        proveedor = Proveedor.objects.get(pk=request.POST.get('proveedor_id'))

        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion="",
            precio_venta=request.POST.get('precio_venta'),
            stock_actual=request.POST.get('cantidad'),
            categoria=categoria,
            proveedor=proveedor,
        )

        return redirect('productos')

    return render(request, 'productos/producto_form.html', {
        'categorias': categorias,
        'proveedores': proveedores
    })

@login_requerido
def editar_producto(request, id):
    producto = get_object_or_404(Producto, producto_id=id)

    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':

        stock_anterior = producto.stock_actual

        nuevo_stock = int(request.POST.get('cantidad'))
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion') or ""
        producto.precio_venta = request.POST.get('precio_venta')
        producto.stock_actual = nuevo_stock
        producto.categoria = Categoria.objects.get(pk=request.POST.get('categoria_id'))
        producto.proveedor = Proveedor.objects.get(pk=request.POST.get('proveedor_id'))
        producto.save()

        diferencia = nuevo_stock - stock_anterior

        if diferencia != 0:
            Movimiento.objects.create(
                producto=producto,
                tipo='entrada' if diferencia > 0 else 'salida',
                cantidad=abs(diferencia)
            )

        return redirect('productos')

    return render(request, 'productos/producto_form.html', {
        'producto': producto,
        'categorias': categorias,
        'proveedores': proveedores
    })

@login_requerido
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, producto_id=id)
    producto.delete()
    return redirect('productos')

@login_requerido
def historial_movimientos(request):
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').all().order_by('-id')
    return render(request, 'inventario/historial.html', {
        'movimientos': movimientos
    })

@login_requerido
def registrar_movimiento(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')

        if not producto_id:
            return render(request, 'inventario/movimiento.html', {
                'productos': productos,
                'error': 'Selecciona un producto'
            })

        producto = Producto.objects.get(pk=producto_id)
        cantidad = int(request.POST.get('cantidad'))
        tipo = request.POST.get('tipo')

        if tipo == 'salida' and producto.stock_actual < cantidad:
            return render(request, 'inventario/movimiento.html', {
                'productos': productos,
                'error': 'No hay suficiente stock'
            })

        if tipo == 'entrada':
            producto.stock_actual += cantidad
        else:
            producto.stock_actual -= cantidad

        producto.save()

        Movimiento.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cantidad,
            fecha=timezone.now()
        )

        return redirect('historial_movimientos')

    return render(request, 'inventario/movimiento.html', {
        'productos': productos
    })

@login_requerido
def empleados(request):
    empleados = Usuario.objects.all()
    return render(request, 'usuarios/empleados.html', {
        'empleados': empleados
    })

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        rol = request.POST.get('rol')

        Usuario.objects.create(
            username=username,
            password_hash=password,
            rol=rol
        )
        return redirect('login')
    return render(request, 'usuarios/empleados_form.html')

@login_requerido
def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes/pacientes.html', {'pacientes': pacientes})

@login_requerido
def agregar_paciente(request):
    if request.method == 'POST':
        nuevo_p = Paciente.objects.create(
            nombre_completo=request.POST.get('nombre'),
            telefono=request.POST.get('telefono'),
            domicilio=request.POST.get('direccion'),
            pasatiempos=request.POST.get('pasatiempos')
        )
        HistoriaClinica.objects.create(paciente=nuevo_p)
        return redirect('pacientes')

    return render(request, 'pacientes/paciente_form.html')

@login_requerido
def historia_clinica(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    historia = get_object_or_404(HistoriaClinica, paciente=paciente)
    ultimo_servicio = ServicioMedico.objects.filter(paciente=paciente).order_by('-fecha').first()

    context = {
        'paciente': paciente,
        'historia': historia,
        'ultimo_servicio': ultimo_servicio
    }
    return render(request, 'pacientes/historia_clinica.html', context)

@login_requerido
def registrar_servicio(request):
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        paciente_obj = get_object_or_404(Paciente, id=paciente_id)

        ServicioMedico.objects.create(
            paciente=paciente_obj,
            notas_refraccion=request.POST.get('descripcion'),
            presion_arterial=request.POST.get('presion_arterial'),
            glucosa=request.POST.get('glucosa'),
            signos_vitales=request.POST.get('signos_vitales')
        )
        return redirect('pacientes')

    pacientes_lista = Paciente.objects.all()
    return render(request, 'pacientes/servicio_medico.html', {'pacientes': pacientes_lista})

@login_requerido
def nueva_venta(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        paciente_id = request.POST.get('cliente')

        producto = get_object_or_404(Producto, id=producto_id)
        paciente = Paciente.objects.filter(id=paciente_id).first() if paciente_id else None

        if producto.stock_actual < cantidad:
            messages.error(request, f"Error: Stock insuficiente. Solo quedan {producto.stock_actual} unidades.")
            return redirect('nueva_venta')

        try:
            with transaction.atomic():
                total_venta = producto.precio_venta * cantidad
                venta = Venta.objects.create(
                    paciente=paciente,
                    total=total_venta,
                    usuario_vendedor_id=request.session.get('usuario_id')
                )

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )

                producto.stock_actual -= cantidad
                producto.save()

                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo_movimiento='salida',
                    cantidad=cantidad,
                    usuario_id=request.session.get('usuario_id')
                )

                messages.success(request, "Venta realizada con éxito e inventario actualizado.")
                return redirect('ventas')

        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {e}")
            return redirect('nueva_venta')

    productos = Producto.objects.filter(stock_actual__gt=0)
    pacientes = Paciente.objects.all()
    return render(request, 'ventas/venta_form.html', {
        'productos': productos,
        'pacientes': pacientes
    })

@login_requerido
def lista_ventas(request):
    ventas = Venta.objects.select_related('paciente', 'usuario').all().order_by('-fecha_venta')
    return render(request, 'ventas/ventas.html', {'ventas': ventas})

@login_requerido
def reportes(request):
    total_ventas = Venta.objects.aggregate(
        Sum('total_venta')
    )['total_venta__sum'] or 0

    return render(request, 'reportes/reportes.html', {
        'total_ventas': total_ventas
    })

@login_requerido
def reporte_grafica(request):
    ventas_mensuales = Venta.objects.annotate(mes=TruncMonth('fecha')) \
        .values('mes') \
        .annotate(total_mes=Sum('total')) \
        .order_by('mes')

    labels = []
    data = []

    for registro in ventas_mensuales:
        nombre_mes = registro['mes'].strftime("%b %Y")
        labels.append(nombre_mes)

        data.append(float(registro['total_mes']))

    context = {
        'labels': labels,
        'data': data,
    }

    return render(request, 'reportes/reporte_grafica.html', context)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Usuario.objects.get(
            username=username,
            password_hash=password
        )

            request.session['usuario_id'] = user.id
            request.session['rol'] = user.rol

            return redirect('dashboard')

        except Usuario.DoesNotExist:
            return render(request, 'usuarios/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'usuarios/login.html')

def logout(request):
    request.session.flush()
    return redirect('login')
