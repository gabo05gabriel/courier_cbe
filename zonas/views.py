# zonas/views.py

from django.shortcuts import render

def lista_zonas(request):
    # Lógica para obtener las zonas
    zonas = []  # Aquí debes obtener las zonas de tu base de datos
    return render(request, 'zonas/lista_zonas.html', {'zonas': zonas})
