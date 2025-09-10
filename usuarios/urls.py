from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('listar/', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('ver/<int:usuario_id>/', views.ver_usuario, name='ver_usuario'),  # Verifica esta línea
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
]
