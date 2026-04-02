from django.shortcuts import render
from django.http import HttpResponse

def inicio(request):
    """App de inicio."""
    return HttpResponse("Bienvenido al Sistema de la Óptica")