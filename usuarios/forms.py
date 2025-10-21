from django import forms
from .models import Usuario, PerfilMensajero
from django.core.exceptions import ValidationError

import re

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'contrasena', 'rol']
        widgets = {
            'contrasena': forms.PasswordInput(render_value=True, attrs={'minlength': '8'}),  # Set min length for password
            'nombre': forms.TextInput(attrs={'maxlength': '15'}),  # Limit the name length
            'telefono': forms.TextInput(attrs={'maxlength': '8', 'pattern': '[0-9]{8}'}),  # Only 7 digits allowed
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.isalpha():
            raise ValidationError('El nombre solo puede contener letras.')
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise ValidationError('El teléfono solo puede contener números.')
        return telefono

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        if len(contrasena) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', contrasena):
            raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'[\W_]', contrasena):
            raise ValidationError('La contraseña debe contener al menos un carácter especial.')
        return contrasena

    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Cifrar la contraseña antes de guardarla
        usuario.set_password(self.cleaned_data['contrasena'])

        if commit:
            usuario.save()
            # Si el rol es Mensajero, crear perfil automáticamente
            if usuario.rol.nombre.lower() == "mensajero":
                PerfilMensajero.objects.get_or_create(usuario=usuario)

        return usuario



class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '********'})
    )
