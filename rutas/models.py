from django.db import models

# Create your models here.
from django.db import models
from usuarios.models import Usuario
from zonas.models import Zona

# Modelo de Rutas
class Ruta(models.Model):
    mensajero = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    duracion_estimada = models.IntegerField(null=True, blank=True)
    duracion_real = models.IntegerField(null=True, blank=True)
    latitud_inicio = models.DecimalField(max_digits=9, decimal_places=6)
    longitud_inicio = models.DecimalField(max_digits=9, decimal_places=6)
    latitud_fin = models.DecimalField(max_digits=9, decimal_places=6)
    longitud_fin = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        unique_together = ('mensajero', 'fecha')

    def __str__(self):
        return f"Ruta {self.ruta_id} - {self.zona.nombre} ({self.fecha})"
