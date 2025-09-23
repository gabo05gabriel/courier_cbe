from django import forms
from .models import Envio, Incidente, Entrega


# ==============================
# Formulario para el modelo Envio
# ==============================
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
            'latitud_origen',
            'longitud_origen',
            'latitud_destino',
            'longitud_destino'
        ]
        widgets = {
            'remitente': forms.Select(attrs={'class': 'form-control'}),
            'origen_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de origen'}),
            'destino_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de destino'}),
            'destinatario_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del destinatario'}),
            'destinatario_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono (7 u 8 dígitos)'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo_servicio': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observaciones adicionales'}),
            'ruta_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'latitud_origen': forms.HiddenInput(),
            'longitud_origen': forms.HiddenInput(),
            'latitud_destino': forms.HiddenInput(),
            'longitud_destino': forms.HiddenInput(),
        }

    # Validación del número de teléfono (Bolivia: 7 u 8 dígitos)
    def clean_destinatario_telefono(self):
        telefono = self.cleaned_data.get('destinatario_telefono')
        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener dígitos.")
        if len(telefono) not in [7, 8]:
            raise forms.ValidationError("El número de teléfono en Bolivia debe tener 7 u 8 dígitos.")
        return telefono


# ==============================
# Formulario para el modelo Incidente
# ==============================
class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['tipo', 'descripcion', 'estado']
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de incidente'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del incidente'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if estado not in ['Pendiente', 'Resuelto']:
            raise forms.ValidationError("El estado debe ser 'Pendiente' o 'Resuelto'.")
        return estado


# ==============================
# Formulario para el modelo Entrega
# ==============================
class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['mensajero', 'estado', 'firma', 'foto']
        widgets = {
            'mensajero': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'firma': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if estado not in ['Entregado', 'Rechazado']:
            raise forms.ValidationError("El estado de la entrega debe ser 'Entregado' o 'Rechazado'.")
        return estado
