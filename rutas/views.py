from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.db import transaction
from django.conf import settings

from .models import Ruta
from usuarios.models import Usuario, PerfilMensajero
from envios.models import Envio
from .services.google_maps import (
    get_route_metrics,
    geocode_address,
    get_polyline_from_ordered_coords
)

import json
import numpy as np

from .routing import (
    compute_algorithmic_route,
    load_delay_model,
    build_time_matrix_with_google
)


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
        # 🔎 Excluir sobres ya entregados
        sobres_qs = Envio.objects.filter(mensajero_id=mensajero_id).exclude(estado="Entregado")
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


# ============================
# Vista: Optimización de rutas
# ============================
def optimizar_rutas(request, mensajero_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Método no soportado")

    mensajero = get_object_or_404(Usuario, pk=mensajero_id)
    perfil = get_object_or_404(PerfilMensajero, usuario=mensajero)

    # 🔎 Envíos pendientes
    envios = Envio.objects.filter(mensajero=mensajero, estado="Pendiente")[:50]
    if not envios:
        return redirect("lista_rutas")

    puntos_json, stops = [], []
    origen_mensajero = None

    try:
        origen_mensajero = (float(perfil.latitud), float(perfil.longitud))
        puntos_json.append({
            "id": f"mensajero-{mensajero.id}",
            "tipo": "Mensajero",
            "lat": origen_mensajero[0],
            "lng": origen_mensajero[1],
            "direccion": "Ubicación inicial del mensajero"
        })
    except (TypeError, ValueError):
        pass

    for envio in envios:
        if envio.tipo == "Recojo" and envio.latitud_origen and envio.longitud_origen:
            try:
                lat, lng = float(envio.latitud_origen), float(envio.longitud_origen)
                puntos_json.append({
                    "id": envio.id,
                    "tipo": "Recojo",
                    "lat": lat, "lng": lng,
                    "direccion": envio.origen_direccion
                })
                stops.append({"id": envio.id, "lat": lat, "lng": lng, "tipo_servicio": envio.tipo_servicio})
            except Exception:
                pass

        elif envio.tipo == "Envío" and envio.latitud_destino and envio.longitud_destino:
            try:
                lat, lng = float(envio.latitud_destino), float(envio.longitud_destino)
                puntos_json.append({
                    "id": envio.id,
                    "tipo": "Envío",
                    "lat": lat, "lng": lng,
                    "direccion": envio.destino_direccion
                })
                stops.append({"id": envio.id, "lat": lat, "lng": lng, "tipo_servicio": envio.tipo_servicio})
            except Exception:
                pass

    if not origen_mensajero or len(stops) < 1:
        return redirect("lista_rutas")

    # ✅ RUTA GOOGLE
    waypoints = [f"{s['lat']},{s['lng']}" for s in stops]
    if len(waypoints) == 1:
        destination = waypoints[0]
        wp = []
    else:
        destination, wp = waypoints[-1], waypoints[:-1]

    dur_google, dist_google, poly_google = get_route_metrics(
        *map(str, origen_mensajero), *destination.split(","), waypoints=wp
    )

    # ✅ RUTA ALGORÍTMICA
    coords = [origen_mensajero] + [(s["lat"], s["lng"]) for s in stops]
    time_matrix = build_time_matrix_with_google(coords, settings.GOOGLE_MAPS_API_KEY)
    delay_model = load_delay_model("delay_tree.joblib")

    algo = compute_algorithmic_route(
        origin=origen_mensajero,
        stops=stops,
        time_matrix=time_matrix,
        delay_model=delay_model
    )

    # Generar polyline/distancia usando el orden calculado
    ordered_coords = [origen_mensajero] + [(s["lat"], s["lng"]) for s in algo["ordered_stops"]]
    poly_algo, dist_algo, dur_algo = get_polyline_from_ordered_coords(
        ordered_coords, settings.GOOGLE_MAPS_API_KEY
    )

    # ✅ RUTA REAL (ficticia zona Sur La Paz)
    ruta_real_coords = [
        (-16.492068944491795, -68.12215947940508),
        (-16.5014610925558, -68.11626541426007),
        (-16.504654052425867, -68.12090028480469),
        (-16.504335835306513, -68.13151440441496),
        (-16.526217571488573, -68.10300852157029),
        (-16.53190336215589, -68.08719283904894),
        (-16.541379307367098, -68.07777874214173),
        (-16.543777573605976, -68.06178499215338),
    ]

    poly_real, dist_real, dur_real = get_polyline_from_ordered_coords(
        ruta_real_coords, settings.GOOGLE_MAPS_API_KEY
    )

    # Guardar rutas en BD
    with transaction.atomic():
        for e in envios:
            Ruta.objects.get_or_create(
                mensajero=mensajero, envio=e,
                defaults=dict(
                    latitud_inicio=e.latitud_origen,
                    longitud_inicio=e.longitud_origen,
                    latitud_fin=e.latitud_destino,
                    longitud_fin=e.longitud_destino
                )
            )

    return render(request, "rutas/optimizar_rutas.html", {
        "ruta_google": {
            "polyline": poly_google,
            "duracion": dur_google,
            "distancia": round(dist_google/1000, 2) if dist_google else None
        },
        "ruta_algo": {
            "polyline": poly_algo,
            "duracion": dur_algo,
            "distancia": round(dist_algo/1000, 2) if dist_algo else None
        },
        "ruta_real": {
            "polyline": poly_real,
            "duracion": dur_real,
            "distancia": round(dist_real/1000, 2) if dist_real else None
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
