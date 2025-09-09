from django import forms
from .models import Zona

class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ['nombre', 'latitud', 'longitud']

        widgets = {
            'latitud': forms.HiddenInput(),   # Para ocultar pero aún enviar
            'longitud': forms.HiddenInput(),
        }
