from urllib import request
from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Proveedor, Movimiento, Usuario
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from functools import wraps


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
    productos = Producto.objects.all()

    total_productos = productos.count()
    stock_bajo = productos.filter(stock_actual__lte=5).count()

    return render(request, 'dashboard.html', {
        'productos': productos[:5],
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
    })

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
    movimientos = Movimiento.objects.select_related('producto').all().order_by('-movimiento_id')
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
            nombre_usuario=username,
            password_hash=password,
            rol=rol
        )
        return redirect('login')
    return render(request, 'usuarios/empleados_form.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Usuario.objects.get(
                nombre_usuario=username,
                password_hash=password
            )

            request.session['usuario_id'] = user.usuario_id
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