# rutas/models.py
from django.db import models
from django.utils import timezone
from usuarios.models import Usuario
from zonas.models import Zona
from envios.models import Envio

class Ruta(models.Model):
    mensajero = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="rutas"
    )
    zona = models.ForeignKey(
        Zona, on_delete=models.SET_NULL, null=True, blank=True, related_name="rutas"
    )
    envio = models.ForeignKey(
        Envio, on_delete=models.SET_NULL, null=True, blank=True, related_name="rutas"
    )

    fecha = models.DateField(auto_now_add=True)

    # Estimado (Google) y Real (app móvil)
    # - duracion_estimada: se llenará automáticamente desde Google (min)
    duracion_estimada = models.IntegerField(null=True, blank=True, help_text="Duración estimada en minutos (Google)")
    # - duracion_real: se llenará luego desde móvil (min)
    duracion_real = models.IntegerField(null=True, blank=True, help_text="Duración real en minutos (app móvil)")

    # Distancia Google (metros) y polyline opcional para dibujar la ruta
    distancia_google_m = models.IntegerField(null=True, blank=True)
    polyline_google = models.TextField(null=True, blank=True)

    # Coordenadas inicio/fin que se fijan en base al tipo del Envío
    latitud_inicio = models.FloatField()
    longitud_inicio = models.FloatField()
    latitud_fin = models.FloatField()
    longitud_fin = models.FloatField()

    # Para ML / clustering
    zona_asignada = models.IntegerField(null=True, blank=True, help_text="Cluster asignado por K-Means")
    retraso_estimado = models.CharField(
        max_length=20, null=True, blank=True,
        choices=[("Retraso estimado", "Retraso estimado"), ("Entrega a tiempo", "Entrega a tiempo")]
    )

    # Timestamps (opcional) para que luego el móvil mande inicios/fin y autocalcules duracion_real
    started_at = models.DateTimeField(null=True, blank=True)    # cuando el mensajero indicó “en camino”
    finished_at = models.DateTimeField(null=True, blank=True)   # cuando indicó “entregado”

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Ruta {self.id} - {self.mensajero.nombre} ({self.fecha})"

    # --- Helpers ---
    def set_coords_from_envio(self):
        """
        Fija lat/lng inicio/fin tomando del Envio. Regla:
        - Para 'Recojo': inicio=origen, fin=destino (recoger y llevar)
        - Para 'Envío' : inicio=origen, fin=destino (ya preparado para entregar)
        Si alguna coord no está, no pisa nada (para evitar romper si faltan datos).
        """
        if not self.envio:
            return

        e = self.envio
        # Solo pisa si hay datos válidos
        if e.origen_lat is not None and e.origen_lng is not None:
            self.latitud_inicio = e.origen_lat
            self.longitud_inicio = e.origen_lng
        if e.destino_lat is not None and e.destino_lng is not None:
            self.latitud_fin = e.destino_lat
            self.longitud_fin = e.destino_lng

    def infer_retraso_simple(self):
        """
        Heurística simple mientras no tengas modelo entrenado:
        Si existe duracion_real y es > duracion_estimada + 10 min => 'Retraso estimado'
        """
        if self.duracion_real and self.duracion_estimada:
            self.retraso_estimado = (
                "Retraso estimado" if self.duracion_real > self.duracion_estimada + 10 else "Entrega a tiempo"
            )

    def recompute_real_duration_from_timestamps(self):
        """
        Si el móvil te manda started_at / finished_at,
        autocalcula duracion_real (en minutos).
        """
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            self.duracion_real = int(delta.total_seconds() // 60)
