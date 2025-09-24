from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ruta del administrador
    path('admin/', admin.site.urls),

    # Redirige la ruta base al login si no estás autenticado
    path('', lambda request: redirect('usuarios:login') if 'usuario_id' not in request.session else redirect('usuarios:home')),  # Redirigir a la vista 'login' de 'usuarios' si no estás autenticado

    # Rutas para la aplicación de envíos
    path('envios/', include('envios.urls')),

    # Rutas para la aplicación de usuarios
    path('usuarios/', include('usuarios.urls')),  # Asegúrate de que esta URL esté incluida

    # Rutas para la aplicación de rutas
    path('rutas/', include('rutas.urls')),

    # Rutas para la aplicación de zonas
    path('zonas/', include('zonas.urls')),

    # Vista de cerrar sesión - Movemos esta URL a 'usuarios' para que esté dentro del espacio de nombres correcto
    path('usuarios/logout/', auth_views.LogoutView.as_view(), name='cerrar_sesion'),  # Vista de cierre de sesión
]

# Agregar la configuración para servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
