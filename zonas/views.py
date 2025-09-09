from django.shortcuts import render, get_object_or_404, redirect
from .models import Zona
from .forms import ZonaForm

# Mostrar la lista de zonas
def lista_zonas(request):
    zonas = Zona.objects.all()
    return render(request, 'zonas/lista_zonas.html', {'zonas': zonas})

# Ver detalle de una zona (con mapa)
def ver_zona(request, zona_id):
    zona = get_object_or_404(Zona, pk=zona_id)
    return render(request, 'zonas/ver_zona.html', {'zona': zona})

# Crear una nueva zona
def crear_zona(request):
    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            # Guardar los valores de latitud y longitud
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')
            zona = form.save(commit=False)
            zona.latitud = latitud
            zona.longitud = longitud
            zona.save()
            return redirect('lista_zonas')
    else:
        form = ZonaForm()

    return render(request, 'zonas/crear_zona.html', {'form': form})