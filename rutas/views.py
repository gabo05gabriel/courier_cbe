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
    # ✅ Solo traer usuarios que son mensajeros
    mensajeros = Usuario.objects.filter(
        id__in=PerfilMensajero.objects.values("usuario_id")
    )

    mensajero_id = request.POST.get("mensajero_id")
    sobres = []

    # ✅ Filtrar sobres según el mensajero seleccionado
    if mensajero_id:
        sobres_qs = Envio.objects.filter(mensajero_id=mensajero_id)
    else:
        sobres_qs = Envio.objects.none()  # vacío si no hay selección

    # ✅ Convertir sobres válidos a JSON con TODOS los campos
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

            # Datos para el mapa
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


# ============================
# Vista: Optimizar y predecir rutas
# ============================
def optimizar_rutas(request, mensajero_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Método no soportado")

    mensajero = get_object_or_404(Usuario, pk=mensajero_id)

    # 🔎 Traer solo envíos pendientes de ese mensajero
    envios = Envio.objects.filter(mensajero=mensajero, estado="Pendiente")[:50]

    if not envios:
        return redirect("lista_rutas")

    # Lista de puntos (recojos y entregas)
    puntos_json = []
    waypoints = []
    for envio in envios:
        if envio.latitud_origen and envio.longitud_origen:
            puntos_json.append({
                "id": envio.id,
                "tipo": "Recojo",
                "lat": float(envio.latitud_origen),
                "lng": float(envio.longitud_origen),
                "direccion": envio.origen_direccion
            })
            waypoints.append(f"{envio.latitud_origen},{envio.longitud_origen}")
        if envio.latitud_destino and envio.longitud_destino:
            puntos_json.append({
                "id": envio.id,
                "tipo": "Entrega",
                "lat": float(envio.latitud_destino),
                "lng": float(envio.longitud_destino),
                "direccion": envio.destino_direccion
            })
            waypoints.append(f"{envio.latitud_destino},{envio.longitud_destino}")

    if len(waypoints) < 2:
        return redirect("lista_rutas")

    # ========= GOOGLE (con waypoints) =========
    origin = waypoints[0]
    destination = waypoints[-1]
    stops = waypoints[1:-1]

    dur_google, dist_google, poly_google = get_route_metrics(
        *origin.split(","), *destination.split(","), waypoints=stops
    )

    # ========= ALGORITMO (heurística básica) =========
    ruta_orden = list(envios)  # aquí podrías ordenar con tu heurística
    poly_algo = ""  # TODO: generar polyline para algoritmo
    dist_algo = 0
    dur_algo = 0

    with transaction.atomic():
        for e in ruta_orden:
            r, _ = Ruta.objects.get_or_create(
                mensajero=mensajero, envio=e,
                defaults=dict(
                    latitud_inicio=e.latitud_origen,
                    longitud_inicio=e.longitud_origen,
                    latitud_fin=e.latitud_destino,
                    longitud_fin=e.longitud_destino
                )
            )
            r.save()

    # ========= REAL (desde móvil, aún vacío) =========
    poly_real = ""
    dur_real = None
    dist_real = None

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
        "puntos": json.dumps(puntos_json, ensure_ascii=False),
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    })



# ============================
# Vista: Ver ruta específica
# ============================
def ver_ruta(request, ruta_id):
    ruta = get_object_or_404(Ruta, id=ruta_id)
    return render(request, "rutas/ver_ruta.html", {"ruta": ruta})
