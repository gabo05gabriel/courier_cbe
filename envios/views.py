import googlemaps
from django.shortcuts import render, redirect, get_object_or_404
from .models import Envio, Incidente, HistorialEnvio, Entrega
from .forms import EnvioForm, IncidenteForm, EntregaForm  # Asegúrate de importar el formulario de Entrega
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
    envios = Envio.objects.all()  # Asegúrate de que no haya un filtro que limite los envíos
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

            # Guardar un historial del envío (evento creado)
            HistorialEnvio.objects.create(
                envio=envio,
                tipo_evento='Creado',
                ubicacion_latitud=lat_origen,
                ubicacion_longitud=lng_origen
            )

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

            # Agregar historial de evento de actualización
            HistorialEnvio.objects.create(
                envio=envio,
                tipo_evento='Actualizado',
                ubicacion_latitud=lat_origen,
                ubicacion_longitud=lng_origen
            )

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

# Vista para registrar un incidente en un envío
def registrar_incidente(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    if request.method == 'POST':
        form = IncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(commit=False)
            incidente.envio = envio  # Asociar el incidente al envío
            incidente.save()

            # Agregar un evento en el historial para el incidente
            HistorialEnvio.objects.create(
                envio=envio,
                tipo_evento='Incidente',
                ubicacion_latitud=envio.latitud_origen,
                ubicacion_longitud=envio.longitud_origen
            )

            return redirect('ver_envio', envio_id=envio.id)  # Redirigir a los detalles del envío
    else:
        form = IncidenteForm()
    return render(request, 'envios/registrar_incidente.html', {'form': form, 'envio': envio})

# Vista para ver los detalles de un incidente
def ver_incidente(request, envio_id, incidente_id):
    envio = get_object_or_404(Envio, id=envio_id)
    incidente = get_object_or_404(Incidente, id=incidente_id)
    return render(request, 'envios/ver_incidente.html', {'incidente': incidente, 'envio': envio})

# Vista para editar un incidente
def editar_incidente(request, envio_id, incidente_id):
    envio = get_object_or_404(Envio, id=envio_id)
    incidente = get_object_or_404(Incidente, id=incidente_id)
    if request.method == 'POST':
        form = IncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            form.save()
            return redirect('ver_incidente', envio_id=envio.id, incidente_id=incidente.id)
    else:
        form = IncidenteForm(instance=incidente)
    return render(request, 'envios/editar_incidente.html', {'form': form, 'envio': envio})

# Vista para eliminar un incidente
def eliminar_incidente(request, envio_id, incidente_id):
    envio = get_object_or_404(Envio, id=envio_id)
    incidente = get_object_or_404(Incidente, id=incidente_id)
    if request.method == 'POST':
        incidente.delete()
        return redirect('ver_envio', envio_id=envio.id)  # Redirigir a la página del envío
    return render(request, 'envios/eliminar_incidente.html', {'incidente': incidente, 'envio': envio})

# Vista para listar entregas
def lista_entregas(request):
    entregas = Entrega.objects.all()  # Obtener todas las entregas de la base de datos
    return render(request, 'envios/lista_entregas.html', {'entregas': entregas})

# Vista para ver los detalles de una entrega
def ver_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    return render(request, 'envios/ver_entrega.html', {'entrega': entrega})

# Vista para registrar una entrega
def registrar_entrega(request, envio_id):
    envio = Envio.objects.get(id=envio_id)  # Get the 'envio' object by ID

    if request.method == "POST":
        form = EntregaForm(request.POST, request.FILES, envio=envio)  # Pass the envio object to the form
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.envio = envio  # Assign the 'envio' to the entrega
            entrega.save()
            return redirect('ver_envio', envio_id=envio.id)  # Redirect to 'ver_envio' after saving
    else:
        form = EntregaForm(envio=envio)  # Pass the envio object to the form

    return render(request, 'envios/registrar_entrega.html', {'form': form, 'envio': envio})
# Vista para editar una entrega
def editar_entrega(request, entrega_id):
    # Obtener la entrega
    entrega = get_object_or_404(Entrega, id=entrega_id)
    
    if request.method == 'POST':
        form = EntregaForm(request.POST, request.FILES, instance=entrega)

        if form.is_valid():
            # Asignar el mensajero antes de guardar
            if not entrega.mensajero:
                entrega.mensajero = request.user  # Asigna el mensajero actual, o el que sea necesario

            # Eliminar las fotos anteriores si el usuario sube nuevas
            if 'firma' in request.FILES:
                if entrega.firma:
                    entrega.firma.delete()

            if 'foto' in request.FILES:
                if entrega.foto:
                    entrega.foto.delete()

            # Guardar los cambios de la entrega
            form.save()

            # Redirigir a la vista de detalles de la entrega
            return redirect('ver_entrega', entrega_id=entrega.id)

    else:
        form = EntregaForm(instance=entrega)

    return render(request, 'envios/editar_entrega.html', {'form': form, 'entrega': entrega})

# Vista para eliminar una entrega
def eliminar_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    if request.method == 'POST':
        entrega.delete()
        return redirect('lista_entregas')  # Redirigir a la lista de entregas
    return render(request, 'envios/eliminar_entrega.html', {'entrega': entrega})

# Vista para ver el historial de un envío
def historial_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)  # Obtener el envío por su ID
    historial = HistorialEnvio.objects.filter(envio=envio)  # Obtener el historial relacionado al envío
    return render(request, 'envios/historial_envio.html', {'envio': envio, 'historial': historial})

# Vista para ver un evento específico en el historial de un envío
def ver_evento_historial(request, envio_id, evento_id):
    # Obtener el envío correspondiente
    envio = get_object_or_404(Envio, id=envio_id)
    
    # Obtener el historial del evento correspondiente
    evento = get_object_or_404(HistorialEnvio, id=evento_id)
    
    return render(request, 'envios/ver_evento_historial.html', {'evento': evento, 'envio': envio})
