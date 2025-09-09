# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),  # Listar usuarios
    path('crear/', views.crear_usuario, name='crear_usuario'),  # Crear usuario
    path('<int:usuario_id>/', views.ver_usuario, name='ver_usuario'),  # Ver detalles del usuario
    path('<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),  # Editar usuario
    path('<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),  # Eliminar usuario
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),  # Cerrar sesión
]
