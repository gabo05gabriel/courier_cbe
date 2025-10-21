from django.shortcuts import render, get_object_or_404, redirect
from .models import Zona
from .forms import ZonaForm

def lista_zonas(request):
    zonas = Zona.objects.all()
    return render(request, 'zonas/lista_zonas.html', {'zonas': zonas})

def ver_zona(request, zona_id):
    zona = get_object_or_404(Zona, id=zona_id)
    return render(request, 'zonas/ver_zona.html', {'zona': zona})

def crear_zona(request):
    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_zonas')
    else:
        form = ZonaForm()
    return render(request, 'zonas/crear_zona.html', {'form': form})

def editar_zona(request, zona_id):
    zona = get_object_or_404(Zona, id=zona_id)
    if request.method == 'POST':
        form = ZonaForm(request.POST, instance=zona)
        if form.is_valid():
            form.save()
            return redirect('lista_zonas')
    else:
        form = ZonaForm(instance=zona)
    return render(request, 'zonas/editar_zona.html', {'form': form, 'zona': zona})

def eliminar_zona(request, zona_id):
    zona = get_object_or_404(Zona, id=zona_id)
    if request.method == 'POST':
        zona.delete()
        return redirect('lista_zonas')
    return render(request, 'zonas/eliminar_zona.html', {'zona': zona})
