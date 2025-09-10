# usuarios/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    contrasena = models.CharField(max_length=255)  # Contraseña cifrada
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # Asegúrate de que el campo is_active exista

    def __str__(self):
        return self.nombre

    def check_password(self, password):
        # Verifica si la contraseña proporcionada coincide con la almacenada
        return check_password(password, self.contrasena)

    def set_password(self, password):
        # Cifra la contraseña antes de guardarla
        self.contrasena = make_password(password)
