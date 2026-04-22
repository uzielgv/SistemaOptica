from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto

def inicio(request):
    return render(request, 'index.html')

def productos(request):
    productos = Producto.objects.all()

    return render(request, 'productos.html', {
        'productos': productos
    })