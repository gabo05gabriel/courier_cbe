from django.db import models
from django.core.files import File
from io import BytesIO
import qrcode
from usuarios.models import Usuario


# ===============================
# 📦 MODELO ENVÍO
# ===============================
class Envio(models.Model):
    tipo = models.CharField(
        max_length=15,
        choices=[('Recojo', 'Recojo'), ('Envío', 'Envío')],
        default='Envío'
    )

    remitente = models.ForeignKey(
    Usuario,
    related_name='remitente',
    on_delete=models.CASCADE,
    null=True, blank=True
)

    remitente_nombre = models.CharField(max_length=150)
    remitente_telefono = models.CharField(max_length=20)

    destinatario_nombre = models.CharField(max_length=150)
    destinatario_telefono = models.CharField(max_length=20)

    origen_direccion = models.TextField()
    destino_direccion = models.TextField()

    peso = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_servicio = models.CharField(
        max_length=15,
        choices=[('Estándar', 'Estándar'), ('Express', 'Express')]
    )

    estado = models.CharField(
        max_length=15,
        default='Pendiente',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Ruta', 'En Ruta'),
            ('Entregado', 'Entregado'),
            ('Rechazado', 'Rechazado'),
            ('Cancelado', 'Cancelado'),
        ]
    )

    observaciones = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    ruta_id = models.IntegerField(null=True, blank=True)

    latitud_origen = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitud_origen = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    latitud_destino = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitud_destino = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)

    monto_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_pago = models.CharField(
        max_length=15,
        choices=[('Origen', 'Origen'), ('Destino', 'Destino')]
    )

    mensajero = models.ForeignKey(
        Usuario,
        related_name='mensajero',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # 🆕 Código QR generado automáticamente
    qr_code = models.ImageField(upload_to='qrcodes/', null=True, blank=True)

    def __str__(self):
        return f"Envío {self.id} - {self.destinatario_nombre}"

    # 🔹 Generar código QR automáticamente al guardar
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda primero para obtener ID

        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=8,
                border=3,
            )

            # URL del envío (ajusta dominio si estás en producción)
            qr.add_data(f"http://127.0.0.1:8000/envios/{self.id}/")
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f'envio_{self.id}_qr.png'
            self.qr_code.save(file_name, File(buffer), save=False)

            super().save(update_fields=['qr_code'])


# ===============================
# 📬 MODELO ENTREGA
# ===============================
class Entrega(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    mensajero = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=15,
        choices=[('Entregado', 'Entregado'), ('Rechazado', 'Rechazado')]
    )
    firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Entrega {self.id} - {self.envio.destinatario_nombre}"


# ===============================
# 🕓 MODELO HISTORIAL DE ENVÍOS
# ===============================
class HistorialEnvio(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    tipo_evento = models.CharField(
        max_length=20,
        choices=[
            ('Creado', 'Creado'),
            ('Asignado', 'Asignado'),
            ('Recogido', 'Recogido'),
            ('Entregado', 'Entregado'),
            ('Incidente', 'Incidente'),
            ('Cancelado', 'Cancelado'),
        ]
    )
    fecha_evento = models.DateTimeField(auto_now_add=True)
    ubicacion_latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    ubicacion_longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Evento {self.tipo_evento} - Envío {self.envio.id}"


# ===============================
# ⚠️ MODELO INCIDENTE
# ===============================
class Incidente(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('Retraso', 'Retraso'),
            ('Daño', 'Daño'),
            ('Pérdida', 'Pérdida'),
            ('Otro', 'Otro')
        ],
        null=True,
        blank=True
    )
    descripcion = models.TextField(null=True, blank=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=15,
        default='Pendiente',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Resuelto', 'Resuelto')
        ],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Incidente {self.tipo or 'Sin tipo'} - Envío {self.envio.id}"
