from django import forms
from .models import Usuario, PerfilMensajero


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'contrasena', 'rol']
        widgets = {
            'contrasena': forms.PasswordInput(render_value=True),  # Ocultar contraseña en el form
        }

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
