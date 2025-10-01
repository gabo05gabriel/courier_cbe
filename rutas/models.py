from django.db import models
from usuarios.models import Usuario
from zonas.models import Zona
from envios.models import Envio


class Ruta(models.Model):
    mensajero = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="rutas"
    )
    zona = models.ForeignKey(
        Zona,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="rutas"
    )
    envio = models.ForeignKey(
        Envio,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="rutas"
    )

    fecha = models.DateField(auto_now_add=True)

    # Datos de tiempos (para predicción de retrasos)
    duracion_estimada = models.IntegerField(null=True, blank=True, help_text="Duración estimada en minutos")
    duracion_real = models.IntegerField(null=True, blank=True, help_text="Duración real en minutos")

    # Coordenadas de inicio y fin (para clustering con K-Means)
    latitud_inicio = models.FloatField()
    longitud_inicio = models.FloatField()
    latitud_fin = models.FloatField()
    longitud_fin = models.FloatField()

    # Resultados de optimización y predicción
    zona_asignada = models.IntegerField(null=True, blank=True, help_text="Cluster asignado por K-Means")
    retraso_estimado = models.CharField(
        max_length=20, null=True, blank=True,
        choices=[("Retraso estimado", "Retraso estimado"), ("Entrega a tiempo", "Entrega a tiempo")]
    )

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Ruta {self.id} - {self.mensajero.nombre} ({self.fecha})"
