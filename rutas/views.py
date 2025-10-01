from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.db import transaction
from django.conf import settings
from .models import Ruta
from usuarios.models import Usuario, PerfilMensajero
from envios.models import Envio

import json
import requests

DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


# ============================
# Servicio: Google Directions con waypoints
# ============================
def get_route_metrics(origin_lat, origin_lng, dest_lat, dest_lng, waypoints=None):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    if not api_key:
        return (None, None, None)

    params = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{dest_lat},{dest_lng}",
        "key": api_key,
        "mode": "driving"
    }
    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    r = requests.get(DIRECTIONS_URL, params=params, timeout=10)
    data = r.json()
    if data.get("status") != "OK":
        return (None, None, None)

    route = data["routes"][0]
    legs = route["legs"]

    duration_sec = sum(leg["duration"]["value"] for leg in legs)
    distance_m = sum(leg["distance"]["value"] for leg in legs)
    polyline = route.get("overview_polyline", {}).get("points")
    return (int(duration_sec // 60), int(distance_m), polyline)


# ============================
# Vista: Lista de sobres/rutas
# ============================
def lista_rutas(request):
    mensajeros = Usuario.objects.filter(
        id__in=PerfilMensajero.objects.values("usuario_id")
    )

    mensajero_id = request.POST.get("mensajero_id")
    sobres = []

    if mensajero_id:
        sobres_qs = Envio.objects.filter(mensajero_id=mensajero_id)
    else:
        sobres_qs = Envio.objects.none()

    for envio in sobres_qs:
        sobres.append({
            "id": envio.id,
            "origen_direccion": envio.origen_direccion,
            "destino_direccion": envio.destino_direccion,
            "destinatario_nombre": envio.destinatario_nombre,
            "destinatario_telefono": envio.destinatario_telefono,
            "peso": str(envio.peso) if envio.peso is not None else None,
            "tipo_servicio": envio.tipo_servicio,
            "estado": envio.estado,
            "observaciones": envio.observaciones,
            "creado_en": envio.creado_en.strftime("%Y-%m-%d %H:%M:%S") if envio.creado_en else None,
            "ruta_id": envio.ruta_id,
            "remitente_id": envio.remitente_id,
            "latitud_destino": float(envio.latitud_destino) if envio.latitud_destino else None,
            "latitud_origen": float(envio.latitud_origen) if envio.latitud_origen else None,
            "longitud_destino": float(envio.longitud_destino) if envio.longitud_destino else None,
            "longitud_origen": float(envio.longitud_origen) if envio.longitud_origen else None,
            "monto_pago": str(envio.monto_pago) if envio.monto_pago else None,
            "tipo": envio.tipo,
            "tipo_pago": envio.tipo_pago,
            "mensajero_id": envio.mensajero_id,
            "remitente_nombre": getattr(envio, "remitente_nombre", None),
            "remitente_telefono": getattr(envio, "remitente_telefono", None),
            "origen": {
                "lat": float(envio.latitud_origen) if envio.latitud_origen else None,
                "lng": float(envio.longitud_origen) if envio.longitud_origen else None,
            },
            "destino": {
                "lat": float(envio.latitud_destino) if envio.latitud_destino else None,
                "lng": float(envio.longitud_destino) if envio.longitud_destino else None,
            },
        })

    return render(request, "rutas/lista_rutas.html", {
        "mensajeros": mensajeros,
        "sobres_json": json.dumps(sobres, ensure_ascii=False),
    })


def optimizar_rutas(request, mensajero_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Método no soportado")

    mensajero = get_object_or_404(Usuario, pk=mensajero_id)
    perfil = get_object_or_404(PerfilMensajero, usuario=mensajero)

    # 🔎 Envíos pendientes
    envios = Envio.objects.filter(mensajero=mensajero, estado="Pendiente")[:50]
    if not envios:
        return redirect("lista_rutas")

    puntos_json = []
    waypoints = []

    # ✅ Punto inicial: ubicación del mensajero
    try:
        origen_mensajero = f"{float(perfil.latitud)},{float(perfil.longitud)}"
    except (TypeError, ValueError):
        origen_mensajero = None

    if origen_mensajero:
        puntos_json.append({
            "id": f"mensajero-{mensajero.id}",
            "tipo": "Mensajero",
            "lat": float(perfil.latitud),
            "lng": float(perfil.longitud),
            "direccion": "Ubicación inicial del mensajero"
        })

    # ✅ Agregar TODOS los puntos de los envíos (Recojo/Envío)
    for envio in envios:
        if envio.tipo == "Recojo" and envio.latitud_origen and envio.longitud_origen:
            try:
                lat, lng = float(envio.latitud_origen), float(envio.longitud_origen)
                puntos_json.append({
                    "id": envio.id,
                    "tipo": "Recojo",
                    "lat": lat,
                    "lng": lng,
                    "direccion": envio.origen_direccion
                })
                waypoints.append(f"{lat},{lng}")
            except (TypeError, ValueError):
                pass

        elif envio.tipo == "Envío" and envio.latitud_destino and envio.longitud_destino:
            try:
                lat, lng = float(envio.latitud_destino), float(envio.longitud_destino)
                puntos_json.append({
                    "id": envio.id,
                    "tipo": "Envío",
                    "lat": lat,
                    "lng": lng,
                    "direccion": envio.destino_direccion
                })
                waypoints.append(f"{lat},{lng}")
            except (TypeError, ValueError):
                pass

    # ✅ limpiar duplicados pero manteniendo el orden
    waypoints = list(dict.fromkeys(waypoints))

    if not origen_mensajero or len(waypoints) < 1:
        return redirect("lista_rutas")

    # ✅ Directions: mensajero como ORIGEN y todos los puntos como paradas
    if len(waypoints) == 1:
        destination = waypoints[0]
        stops = []
    else:
        destination = waypoints[-1]
        stops = waypoints[:-1]

    dur_google, dist_google, poly_google = get_route_metrics(
        *origen_mensajero.split(","), *destination.split(","), waypoints=stops
    )

    # ========= ALGORITMO (placeholder) =========
    ruta_orden = list(envios)
    poly_algo, dist_algo, dur_algo = "", 0, 0

    with transaction.atomic():
        for e in ruta_orden:
            Ruta.objects.get_or_create(
                mensajero=mensajero, envio=e,
                defaults=dict(
                    latitud_inicio=e.latitud_origen,
                    longitud_inicio=e.longitud_origen,
                    latitud_fin=e.latitud_destino,
                    longitud_fin=e.longitud_destino
                )
            )

    # ========= REAL (vacío) =========
    poly_real, dur_real, dist_real = "", None, None

    # ========= JSON espejo de lista_rutas =========
    envios_json_data = []
    for envio in envios:
        envios_json_data.append({
            "id": envio.id,
            "origen_direccion": envio.origen_direccion,
            "destino_direccion": envio.destino_direccion,
            "destinatario_nombre": envio.destinatario_nombre,
            "destinatario_telefono": envio.destinatario_telefono,
            "peso": str(envio.peso) if getattr(envio, "peso", None) is not None else None,
            "tipo_servicio": envio.tipo_servicio,
            "estado": envio.estado,
            "observaciones": envio.observaciones,
            "creado_en": envio.creado_en.strftime("%Y-%m-%d %H:%M:%S") if getattr(envio, "creado_en", None) else None,
            "ruta_id": envio.ruta_id,
            "remitente_id": envio.remitente_id,
            "latitud_destino": float(envio.latitud_destino) if getattr(envio, "latitud_destino", None) else None,
            "latitud_origen": float(envio.latitud_origen) if getattr(envio, "latitud_origen", None) else None,
            "longitud_destino": float(envio.longitud_destino) if getattr(envio, "longitud_destino", None) else None,
            "longitud_origen": float(envio.longitud_origen) if getattr(envio, "longitud_origen", None) else None,
            "monto_pago": str(envio.monto_pago) if getattr(envio, "monto_pago", None) else None,
            "tipo": envio.tipo,
            "tipo_pago": envio.tipo_pago,
            "mensajero_id": envio.mensajero_id,
            "remitente_nombre": getattr(envio, "remitente_nombre", None),
            "remitente_telefono": getattr(envio, "remitente_telefono", None),
            "origen": {
                "lat": float(envio.latitud_origen) if getattr(envio, "latitud_origen", None) else None,
                "lng": float(envio.longitud_origen) if getattr(envio, "longitud_origen", None) else None,
            },
            "destino": {
                "lat": float(envio.latitud_destino) if getattr(envio, "latitud_destino", None) else None,
                "lng": float(envio.longitud_destino) if getattr(envio, "longitud_destino", None) else None,
            },
        })

    return render(request, "rutas/optimizar_rutas.html", {
        "ruta_google": {
            "polyline": poly_google,
            "duracion": dur_google,
            "distancia": round(dist_google/1000, 2) if dist_google else None
        },
        "ruta_algo": {
            "polyline": poly_algo,
            "duracion": dur_algo,
            "distancia": dist_algo
        },
        "ruta_real": {
            "polyline": poly_real,
            "duracion": dur_real,
            "distancia": dist_real
        },
        "puntos": json.dumps(puntos_json, ensure_ascii=False),   # ✅ incluye TODOS
        "envios_json": json.dumps(envios_json_data, ensure_ascii=False),
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    })

# ============================
# Vista: Ver ruta específica
# ============================
def ver_ruta(request, ruta_id):
    ruta = get_object_or_404(Ruta, id=ruta_id)
    return render(request, "rutas/ver_ruta.html", {"ruta": ruta})
