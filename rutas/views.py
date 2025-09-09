# rutas/views.py

from django.shortcuts import render

def lista_rutas(request):
    # Lógica para obtener las rutas
    rutas = []  # Aquí debes obtener las rutas de tu base de datos
    return render(request, 'rutas/lista_rutas.html', {'rutas': rutas})
