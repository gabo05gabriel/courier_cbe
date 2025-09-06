import googlemaps
from django.shortcuts import render, redirect, get_object_or_404
from .models import Envio
from .forms import EnvioForm
from django.conf import settings

# Configura tu clave API de Google Maps
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

# Función para obtener las coordenadas de una dirección
def obtener_coordenadas(direccion):
    geocode_result = gmaps.geocode(direccion)
    if geocode_result:
        latitud = geocode_result[0]['geometry']['location']['lat']
        longitud = geocode_result[0]['geometry']['location']['lng']
        return latitud, longitud
    return None, None

# Vista para listar los envíos
def lista_envios(request):
    envios = Envio.objects.all()  # Obtener todos los envíos de la base de datos
    return render(request, 'envios/lista_envios.html', {'envios': envios})

# Vista para crear un nuevo envío
def crear_envio(request):
    if request.method == 'POST':
        form = EnvioForm(request.POST)
        if form.is_valid():
            # Obtener las coordenadas de origen y destino usando la API de Google Maps
            origen = form.cleaned_data['origen_direccion']
            destino = form.cleaned_data['destino_direccion']
            lat_origen, lng_origen = obtener_coordenadas(origen)
            lat_destino, lng_destino = obtener_coordenadas(destino)

            # Guardar el nuevo envío con las coordenadas obtenidas
            envio = form.save(commit=False)
            envio.latitud_origen = lat_origen
            envio.longitud_origen = lng_origen
            envio.latitud_destino = lat_destino
            envio.longitud_destino = lng_destino
            envio.save()

            return redirect('lista_envios')  # Redirigir a la lista de envíos
    else:
        form = EnvioForm()
    return render(request, 'envios/crear_envio.html', {'form': form})

# Vista para ver los detalles de un envío
def ver_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)  # Obtener el envío por su ID
    return render(request, 'envios/ver_envio.html', {'envio': envio})

# Vista para editar un envío
def editar_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)  # Obtener el envío por su ID
    if request.method == 'POST':
        form = EnvioForm(request.POST, instance=envio)
        if form.is_valid():
            # Obtener las coordenadas de origen y destino usando la API de Google Maps
            origen = form.cleaned_data['origen_direccion']
            destino = form.cleaned_data['destino_direccion']
            lat_origen, lng_origen = obtener_coordenadas(origen)
            lat_destino, lng_destino = obtener_coordenadas(destino)

            # Guardar el envío editado con las nuevas coordenadas
            envio = form.save(commit=False)
            envio.latitud_origen = lat_origen
            envio.longitud_origen = lng_origen
            envio.latitud_destino = lat_destino
            envio.longitud_destino = lng_destino
            envio.save()

            return redirect('lista_envios')  # Redirigir a la lista de envíos
    else:
        form = EnvioForm(instance=envio)
    return render(request, 'envios/editar_envio.html', {'form': form})

# Vista para eliminar un envío
def eliminar_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)  # Obtener el envío por su ID
    if request.method == 'POST':
        envio.delete()
        return redirect('lista_envios')  # Redirigir a la lista de envíos
    return render(request, 'envios/eliminar_envio.html', {'envio': envio})
