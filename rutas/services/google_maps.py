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

def get_polyline_from_ordered_coords(coords, api_key):
    """
    Dibuja una ruta en el orden exacto de coords usando Directions API.
    coords: [(lat, lng), ...] en el orden de la ruta
    Retorna: polyline, distancia (m), duración (min)
    """
    if not api_key or len(coords) < 2:
        return None, None, None

    origin = f"{coords[0][0]},{coords[0][1]}"
    destination = f"{coords[-1][0]},{coords[-1][1]}"
    waypoints = [f"{lat},{lng}" for lat, lng in coords[1:-1]]

    params = {
        "origin": origin,
        "destination": destination,
        "key": api_key,
        "mode": "driving",
        "waypoints": "|".join(waypoints) if waypoints else None
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        r = requests.get(DIRECTIONS_URL, params=params, timeout=10).json()
        if r.get("status") != "OK":
            return None, None, None

        route = r["routes"][0]
        legs = route["legs"]
        dur = sum(leg["duration"]["value"] for leg in legs) // 60  # minutos
        dist = sum(leg["distance"]["value"] for leg in legs)       # metros
        polyline = route.get("overview_polyline", {}).get("points")
        return polyline, dist, dur
    except Exception:
        return None, None, None
