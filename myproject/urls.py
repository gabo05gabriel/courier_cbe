from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Importa auth_views


urlpatterns = [
    # Ruta para el panel de administración de Django
    path('admin/', admin.site.urls),

    # Ruta para la lista de envíos directamente
    path('', include('envios.urls')),  # Solo incluye las rutas de la aplicación envios

    # URLs para la aplicación de envíos
    path('envios/', include('envios.urls')),  # Incluye las rutas de la aplicación envios

    # URLs para la aplicación de usuarios
    path('usuarios/', include('usuarios.urls')),  # Incluye las rutas de la aplicación usuarios

    # URLs para la aplicación de rutas
    path('rutas/', include('rutas.urls')),  # Asegúrate de incluir las URLs de rutas

    # URLs para la aplicación de zonas
    path('zonas/', include('zonas.urls')),  # Asegúrate de incluir las rutas de zonas

    # Vista de cerrar sesión
    path('logout/', auth_views.LogoutView.as_view(), name='cerrar_sesion'),  # Vista de cerrar sesión

    # Si tienes otras aplicaciones, agrega las rutas aquí
    # path('otros/', include('otros.urls')),  # Incluye las rutas de la aplicación otros
]
