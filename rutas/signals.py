# rutas/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Ruta
from .services.google_maps import get_route_metrics

@receiver(pre_save, sender=Ruta)
def rutas_set_coords_and_google_estimate(sender, instance: Ruta, **kwargs):
    # Si viene con Envio, llena coords (si están vacías)
    if instance.envio:
        # Solo si no están definidas aún
        if instance.latitud_inicio is None or instance.longitud_inicio is None \
           or instance.latitud_fin is None or instance.longitud_fin is None:
            instance.set_coords_from_envio()

    # Si hay coords completas, pide métricas a Google
    if all([
        instance.latitud_inicio is not None, instance.longitud_inicio is not None,
        instance.latitud_fin is not None, instance.longitud_fin is not None
    ]):
        dur_min, dist_m, poly = get_route_metrics(
            instance.latitud_inicio, instance.longitud_inicio,
            instance.latitud_fin, instance.longitud_fin
        )
        if dur_min is not None:
            instance.duracion_estimada = dur_min
        if dist_m is not None:
            instance.distancia_google_m = dist_m
        if poly:
            instance.polyline_google = poly

@receiver(post_save, sender=Ruta)
def rutas_infer_delay(sender, instance: Ruta, **kwargs):
    # Si ya existe duracion_real (cuando el móvil lo mande), infiere retraso
    instance.infer_retraso_simple()
    # Evita loop infinito: solo guarda si cambió la etiqueta y está seteada
    if instance.retraso_estimado:
        Ruta.objects.filter(pk=instance.pk).update(retraso_estimado=instance.retraso_estimado)
