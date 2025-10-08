import base64
import qrcode
import googlemaps
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Envio, Incidente, HistorialEnvio, Entrega
from .forms import EnvioForm, IncidenteForm, EntregaForm


# ===============================
# 🔑 CONFIGURACIÓN GOOGLE MAPS
# ===============================
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)


# ===============================
# 📍 FUNCIONES AUXILIARES
# ===============================
def obtener_coordenadas(direccion):
    """Obtiene latitud y longitud a partir de una dirección usando Google Maps API."""
    direccion_completa = f"{direccion}, La Paz, Bolivia"
    geocode_result = gmaps.geocode(direccion_completa)
    if geocode_result:
        latitud = geocode_result[0]['geometry']['location']['lat']
        longitud = geocode_result[0]['geometry']['location']['lng']
        return latitud, longitud
    return None, None


# ===============================
# 📦 ENVÍOS
# ===============================
def lista_envios(request):
    envios = Envio.objects.all()
    return render(request, 'envios/lista_envios.html', {'envios': envios})


def crear_envio(request):
    if request.method == 'POST':
        form = EnvioForm(request.POST)
        if form.is_valid():
            envio = form.save(commit=False)

            # Si vienen coordenadas en el formulario, las usamos
            if request.POST.get("latitud_origen") and request.POST.get("longitud_origen"):
                envio.latitud_origen = request.POST.get("latitud_origen")
                envio.longitud_origen = request.POST.get("longitud_origen")

            if request.POST.get("latitud_destino") and request.POST.get("longitud_destino"):
                envio.latitud_destino = request.POST.get("latitud_destino")
                envio.longitud_destino = request.POST.get("longitud_destino")

            envio.save()

            return redirect('lista_envios')
    else:
        form = EnvioForm()
    return render(request, 'envios/crear_envio.html', {'form': form})
    
def ver_envio(request, envio_id):
    """Muestra la guía del envío con QR dinámico y mapa."""
    envio = get_object_or_404(Envio, id=envio_id)

    # Generar QR dinámico sin almacenarlo
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=2,
    )
    qr.add_data(request.build_absolute_uri())  # URL actual del envío
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'envios/ver_envio.html', {
        'envio': envio,
        'qr_base64': qr_base64
    })


def editar_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)

    if request.method == 'POST':
        form = EnvioForm(request.POST, instance=envio)
        if form.is_valid():
            envio = form.save(commit=False)

            lat_origen = request.POST.get("latitud_origen")
            lng_origen = request.POST.get("longitud_origen")
            lat_destino = request.POST.get("latitud_destino")
            lng_destino = request.POST.get("longitud_destino")

            if lat_origen and lng_origen:
                envio.latitud_origen = float(lat_origen)
                envio.longitud_origen = float(lng_origen)
            else:
                envio.latitud_origen, envio.longitud_origen = obtener_coordenadas(envio.origen_direccion)

            if lat_destino and lng_destino:
                envio.latitud_destino = float(lat_destino)
                envio.longitud_destino = float(lng_destino)
            else:
                envio.latitud_destino, envio.longitud_destino = obtener_coordenadas(envio.destino_direccion)

            envio.save()

            HistorialEnvio.objects.create(
                envio=envio,
                tipo_evento='Actualizado',
                ubicacion_latitud=envio.latitud_origen,
                ubicacion_longitud=envio.longitud_origen
            )

            messages.success(request, "Envío actualizado correctamente.")
            return redirect('lista_envios')
    else:
        form = EnvioForm(instance=envio)

    return render(request, 'envios/editar_envio.html', {'form': form, 'envio': envio})


def eliminar_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    if request.method == 'POST':
        envio.delete()
        return redirect('lista_envios')
    return render(request, 'envios/eliminar_envio.html', {'envio': envio})


# ===============================
# ⚠️ INCIDENTES
# ===============================
def registrar_incidente(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    if request.method == 'POST':
        form = IncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(commit=False)
            incidente.envio = envio
            incidente.save()

            HistorialEnvio.objects.create(
                envio=envio,
                tipo_evento='Incidente',
                ubicacion_latitud=envio.latitud_origen,
                ubicacion_longitud=envio.longitud_origen
            )
            return redirect('ver_envio', envio_id=envio.id)
    else:
        form = IncidenteForm()
    return render(request, 'envios/registrar_incidente.html', {'form': form, 'envio': envio})


def ver_incidente(request, envio_id, incidente_id):
    envio = get_object_or_404(Envio, id=envio_id)
    incidente = get_object_or_404(Incidente, id=incidente_id)
    return render(request, 'envios/ver_incidente.html', {'incidente': incidente, 'envio': envio})


def editar_incidente(request, envio_id, incidente_id):
    envio = get_object_or_404(Envio, id=envio_id)
    incidente = get_object_or_404(Incidente, id=incidente_id)
    if request.method == 'POST':
        form = IncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            form.save()
            messages.success(request, "Incidente actualizado correctamente.")
            return redirect('ver_incidente', envio_id=envio.id, incidente_id=incidente.id)
    else:
        form = IncidenteForm(instance=incidente)
    return render(request, 'envios/editar_incidente.html', {'form': form, 'envio': envio})


def eliminar_incidente(request, envio_id, incidente_id):
    envio = get_object_or_404(Envio, id=envio_id)
    incidente = get_object_or_404(Incidente, id=incidente_id)
    if request.method == 'POST':
        incidente.delete()
        return redirect('ver_envio', envio_id=envio.id)
    return render(request, 'envios/eliminar_incidente.html', {'incidente': incidente, 'envio': envio})


# ===============================
# 📬 ENTREGAS
# ===============================
def lista_entregas(request):
    entregas = Entrega.objects.all()
    return render(request, 'envios/lista_entregas.html', {'entregas': entregas})


def ver_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    return render(request, 'envios/ver_entrega.html', {'entrega': entrega})


def registrar_entrega(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    if request.method == 'POST':
        form = EntregaForm(request.POST, request.FILES)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.envio = envio
            entrega.mensajero = envio.mensajero
            entrega.save()

            # Si el formulario incluye incidente
            tipo = request.POST.get('tipo_incidente')
            descripcion = request.POST.get('descripcion_incidente')
            if tipo or descripcion:
                Incidente.objects.create(
                    envio=envio,
                    tipo=tipo or 'Otro',
                    descripcion=descripcion or ''
                )

            messages.success(request, "Entrega registrada correctamente.")
            return redirect('ver_envio', envio.id)
        else:
            print("❌ ERRORES DE FORMULARIO:", form.errors)
            messages.error(request, "Hubo un error en el formulario.")
    else:
        form = EntregaForm()
    return render(request, 'envios/registrar_entrega.html', {'form': form, 'envio': envio})


def editar_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    if request.method == 'POST':
        form = EntregaForm(request.POST, request.FILES, instance=entrega)
        if form.is_valid():
            form.save()
            messages.success(request, "Entrega actualizada correctamente.")
            return redirect('ver_entrega', entrega_id=entrega.id)
    else:
        form = EntregaForm(instance=entrega)
    return render(request, 'entregas/editar_entrega.html', {'form': form, 'entrega': entrega})


def eliminar_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    if request.method == 'POST':
        entrega.delete()
        return redirect('lista_entregas')
    return render(request, 'envios/eliminar_entrega.html', {'entrega': entrega})


# ===============================
# 🕓 HISTORIAL
# ===============================
def historial_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    historial = HistorialEnvio.objects.filter(envio=envio)
    return render(request, 'envios/historial_envio.html', {'envio': envio, 'historial': historial})


def ver_evento_historial(request, envio_id, evento_id):
    envio = get_object_or_404(Envio, id=envio_id)
    evento = get_object_or_404(HistorialEnvio, id=evento_id)
    return render(request, 'envios/ver_evento_historial.html', {'evento': evento, 'envio': envio})
