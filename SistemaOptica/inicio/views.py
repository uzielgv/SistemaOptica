from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Proveedor

def inicio(request):
    return render(request, 'base.html')


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

        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion') or ""
        producto.precio_venta = request.POST.get('precio_venta')
        producto.stock_actual = request.POST.get('cantidad')

        producto.categoria = Categoria.objects.get(pk=request.POST.get('categoria_id'))
        producto.proveedor = Proveedor.objects.get(pk=request.POST.get('proveedor_id'))

        producto.save()

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

def dashboard(request):
    productos = Producto.objects.all()

    total_productos = productos.count()
    stock_bajo = productos.filter(stock_actual__lte=5).count()

    return render(request, 'dashboard.html', {
        'productos': productos[:5],
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
    })