from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),  # Aquí se usa '' para la lista de usuarios
    path('crear/', views.crear_usuario, name='crear_usuario'),  # Para crear un usuario
    path('<int:usuario_id>/', views.ver_usuario, name='ver_usuario'),  # Para ver un usuario específico
    path('<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),  # Para editar un usuario
    path('<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),  # Para eliminar un usuario
]
