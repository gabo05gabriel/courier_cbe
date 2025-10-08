from django.urls import path
from . import views

# Namespace para esta app
app_name = 'usuarios'

urlpatterns = [
    # CRUD de usuarios
    path('listar/', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('ver/<int:usuario_id>/', views.ver_usuario, name='ver_usuario'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    # Página de inicio
    path('home/', views.home, name='home'),

    # Nuevo: Vista de mensajeros en tiempo real
    path('mensajeros/', views.mensajeros_view, name='mensajeros'),
    path('api/login/', views.api_login, name='api_login'),  # ✅ NUEVO ENDPOINT
    path('home_data/', views.home_data, name='home_data'),

]
