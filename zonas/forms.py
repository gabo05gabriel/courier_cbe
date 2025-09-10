from django import forms
from .models import Zona

class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ['nombre', 'area']
        widgets = {
            'area': forms.Textarea(attrs={'placeholder': 'Introduce las coordenadas como un array JSON'}),
        }
