from django.urls import path
from . import views

urlpatterns = [
    path('envios/', views.lista_envios, name='lista_envios'),
    path('envios/crear/', views.crear_envio, name='crear_envio'),
    path('envios/<int:envio_id>/', views.ver_envio, name='ver_envio'),
    path('envios/<int:envio_id>/editar/', views.editar_envio, name='editar_envio'),
    path('envios/<int:envio_id>/eliminar/', views.eliminar_envio, name='eliminar_envio'),
]
