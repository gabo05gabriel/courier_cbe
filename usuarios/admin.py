# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Esta es la referencia correcta a 'admin'
    path('usuarios/', include('usuarios.urls')),  # Rutas de la aplicación 'usuarios'
]
