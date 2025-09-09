from django import forms
from .models import Envio, Incidente, Entrega

# Formulario para el modelo Envio
class EnvioForm(forms.ModelForm):
    class Meta:
        model = Envio
        fields = [
            'remitente', 
            'origen_direccion', 
            'destino_direccion', 
            'destinatario_nombre', 
            'destinatario_telefono', 
            'peso', 
            'tipo_servicio', 
            'estado', 
            'observaciones', 
            'ruta_id', 
            'latitud_origen',  # Campo de latitud de origen
            'longitud_origen',  # Campo de longitud de origen
            'latitud_destino',  # Campo de latitud de destino
            'longitud_destino'  # Campo de longitud de destino
        ]
        # Si deseas agregar widgets o validación adicional, puedes hacerlo aquí
        widgets = {
            'origen_direccion': forms.TextInput(attrs={'placeholder': 'Dirección de origen'}),
            'destino_direccion': forms.TextInput(attrs={'placeholder': 'Dirección de destino'}),
            'destinatario_telefono': forms.TextInput(attrs={'placeholder': 'Número de teléfono'}),
            'observaciones': forms.Textarea(attrs={'placeholder': 'Observaciones adicionales'}),
        }

    # Validación del número de teléfono
    def clean_destinatario_telefono(self):
        telefono = self.cleaned_data.get('destinatario_telefono')
        if len(telefono) < 10:
            raise forms.ValidationError("El número de teléfono debe tener al menos 10 caracteres.")
        return telefono


# Formulario para el modelo Incidente
class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['tipo', 'descripcion', 'estado']

    # Validación del estado del incidente
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if estado not in ['Pendiente', 'Resuelto']:
            raise forms.ValidationError("El estado debe ser 'Pendiente' o 'Resuelto'.")
        return estado


# Formulario para el modelo Entrega (corregido)
class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['estado', 'firma', 'foto']  # No incluir 'fecha_entrega' ya que es no editable

    # Validación del estado de entrega
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if estado not in ['Entregado', 'Rechazado']:
            raise forms.ValidationError("El estado de la entrega debe ser 'Entregado' o 'Rechazado'.")
        return estado
