from django.shortcuts import render
from .models import Ruta

def lista_rutas(request):
    rutas = Ruta.objects.all()
    return render(request, 'rutas/lista_rutas.html', {'rutas': rutas})
