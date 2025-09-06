from django import forms
from .models import Envio

class EnvioForm(forms.ModelForm):
    class Meta:
        model = Envio
        fields = ['remitente', 'origen_direccion', 'destino_direccion', 'destinatario_nombre', 'destinatario_telefono', 'peso', 'tipo_servicio', 'estado', 'observaciones', 'ruta_id']
