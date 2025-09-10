from django.db import models
from usuarios.models import Usuario

# Modelo de Envíos
class Envio(models.Model):
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario remitente
    origen_direccion = models.TextField()
    destino_direccion = models.TextField()
    destinatario_nombre = models.CharField(max_length=150)
    destinatario_telefono = models.CharField(max_length=20)
    peso = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_servicio = models.CharField(max_length=15, choices=[('Estándar', 'Estándar'), ('Express', 'Express')])
    estado = models.CharField(max_length=15, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('En Ruta', 'En Ruta'), ('Entregado', 'Entregado'), ('Rechazado', 'Rechazado'), ('Cancelado', 'Cancelado')])
    observaciones = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    ruta_id = models.IntegerField(null=True, blank=True)  # Relación con la ruta si es necesario
    
    # Agregar latitud y longitud para origen y destino
    latitud_origen = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitud_origen = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    latitud_destino = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitud_destino = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)

    def __str__(self):
        return f"Envio {self.id} - {self.destinatario_nombre}"

# Modelo de Entregas
class Entrega(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)  # Relación con Envio
    mensajero = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relación con Usuario (mensajero)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=[('Entregado', 'Entregado'), ('Rechazado', 'Rechazado')])
    firma = models.ImageField(upload_to='firmas/', null=True, blank=True)  # Firma de entrega
    foto = models.ImageField(upload_to='fotos/', null=True, blank=True)  # Foto de entrega

    def __str__(self):
        return f"Entrega {self.id} - {self.envio.destinatario_nombre}"

# Modelo de Historial de Envíos
class HistorialEnvio(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)  # Relación con Envio
    tipo_evento = models.CharField(max_length=20, choices=[('Creado', 'Creado'), ('Asignado', 'Asignado'), ('Recogido', 'Recogido'), ('Entregado', 'Entregado'), ('Incidente', 'Incidente'), ('Cancelado', 'Cancelado')])
    fecha_evento = models.DateTimeField(auto_now_add=True)
    ubicacion_latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    ubicacion_longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Evento {self.tipo_evento} - Envío {self.envio.id}"

# Modelo de Incidentes
class Incidente(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)  # Relación con Envio
    tipo = models.CharField(max_length=20, choices=[('Retraso', 'Retraso'), ('Daño', 'Daño'), ('Pérdida', 'Pérdida'), ('Otro', 'Otro')])
    descripcion = models.TextField()  # Descripción del incidente
    fecha_reporte = models.DateTimeField(auto_now_add=True)  # Fecha en que se reporta el incidente
    estado = models.CharField(max_length=15, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Resuelto', 'Resuelto')])

    def __str__(self):
        return f"Incidente {self.tipo} - Envío {self.envio.id}"
