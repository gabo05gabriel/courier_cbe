import requests
from django.conf import settings

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


def geocode_address(address: str):
    """
    Convierte una dirección (texto) en coordenadas (lat, lng) usando Google Maps Geocoding API.
    Retorna (lat, lng) o (None, None) si falla.
    """
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    if not api_key or not address:
        return (None, None)

    params = {
        "address": address,
        "key": api_key
    }
    try:
        r = requests.get(GEOCODE_URL, params=params, timeout=10)
        data = r.json()
        if data.get("status") != "OK":
            return (None, None)

        location = data["results"][0]["geometry"]["location"]
        return (location["lat"], location["lng"])
    except Exception:
        return (None, None)


def get_route_metrics(origin_lat, origin_lng, dest_lat, dest_lng, waypoints=None):
    """
    Obtiene distancia, duración y polyline de Directions API con waypoints opcionales.
    """
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

    try:
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
    except Exception:
        return (None, None, None)

