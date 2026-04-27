from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Proveedor, Movimiento
from django.utils import timezone


def inicio(request):
    return render(request, 'base.html')

def dashboard(request):
    productos = Producto.objects.all()

    total_productos = productos.count()
    stock_bajo = productos.filter(stock_actual__lte=5).count()

    return render(request, 'dashboard.html', {
        'productos': productos[:5],
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
    })

def productos(request):
    productos = Producto.objects.select_related('categoria', 'proveedor').all()
    print(Producto.objects.all())
    print(productos)
    print(request.POST)
    return render(request, 'productos/productos.html', {
        'productos': productos
    })

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

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, producto_id=id)
    producto.delete()
    return redirect('productos')

def historial_movimientos(request):
    movimientos = Movimiento.objects.select_related('producto').all().order_by('-movimiento_id')
    return render(request, 'inventario/historial.html', {
        'movimientos': movimientos
    })

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