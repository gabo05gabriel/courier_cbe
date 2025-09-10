from django.shortcuts import render, redirect, get_object_or_404
from .forms import ZonaForm
from .models import Zona
import json

def lista_zonas(request):
    # Obtener todas las zonas de la base de datos
    zonas = Zona.objects.all()  
    return render(request, 'zonas/lista_zonas.html', {'zonas': zonas})

def crear_zona(request):
    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            # Guardar la nueva zona
            zona = form.save(commit=False)
            
            # Obtener las coordenadas del polígono desde el campo 'zona_area' en el formulario
            zona_area = request.POST.get('zona_area')
            if zona_area:
                zona.set_area_from_list(json.loads(zona_area))  # Convertir las coordenadas de JSON a lista y guardarlas en 'area'
            
            zona.save()  # Guardar la zona con el área
            
            return redirect('lista_zonas')  # Redirigir a la lista de zonas
    else:
        form = ZonaForm()  # Si es GET, crear un formulario vacío

    # Renderizar la plantilla 'crear_zona.html' con el formulario
    return render(request, 'zonas/crear_zona.html', {'form': form})

def ver_zona(request, zona_id):
    # Obtener la zona por ID
    zona = get_object_or_404(Zona, id=zona_id)

    # Verificar si el área tiene coordenadas y manejarlas correctamente
    try:
        # Convertimos las coordenadas de área a una lista de Python
        area_coordinates = json.loads(zona.area) if zona.area else []
    except json.JSONDecodeError:
        area_coordinates = []  # Si hay un error de JSON, devolvemos un arreglo vacío

    # Pasamos los datos a la plantilla
    return render(request, 'zonas/ver_zona.html', {'zona': zona, 'area_coordinates': area_coordinates})