from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('lista_envios')),  # Redirige a la página de envíos
    path('envios/', include('envios.urls')),  # URLs para la aplicación de envíos
    path('usuarios/', include('usuarios.urls')),  # URLs para la aplicación de usuarios
]
