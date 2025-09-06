from django.db import models

# Modelo de Zonas
class Zona(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
