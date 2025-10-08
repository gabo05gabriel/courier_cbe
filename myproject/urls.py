from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# Importar vistas de JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # 🔹 Redirigir raíz según sesión de usuario (solo interfaz web)
    path(
        '',
        lambda request: redirect('usuarios:login')
        if 'usuario_id' not in request.session
        else redirect('usuarios:home'),
    ),

    # 🔹 Módulos internos del sistema web
    path('envios/', include('envios.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('rutas/', include('rutas.urls')),
    path('zonas/', include('zonas.urls')),

    # 🔹 Cierre de sesión del panel web
    path('usuarios/logout/', auth_views.LogoutView.as_view(), name='cerrar_sesion'),

    # 🔹 API para autenticación JWT (para Flutter)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🔹 Endpoint de prueba autenticado
    path('api/', include('envios.urls')),  # ejemplo: /api/me/
]

# 🔹 Servir archivos de medios durante desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
