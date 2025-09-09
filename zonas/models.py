from django.db import models

class Zona(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    latitud = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitud = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)

    def __str__(self):
        return self.nombre
