from django.urls import path
from . import views

urlpatterns = [
    # Rutas para envíos
    path('', views.lista_envios, name='lista_envios'),  # Lista de envíos (página principal)
    path('envios/crear/', views.crear_envio, name='crear_envio'),  # Crear un nuevo envío
    path('envios/<int:envio_id>/', views.ver_envio, name='ver_envio'),  # Ver detalles de un envío
    path('envios/<int:envio_id>/editar/', views.editar_envio, name='editar_envio'),  # Editar un envío
    path('envios/<int:envio_id>/eliminar/', views.eliminar_envio, name='eliminar_envio'),  # Eliminar un envío

    # Rutas para entregas
    path('entregas/', views.lista_entregas, name='lista_entregas'),  # Lista de entregas
    path('entregas/crear/<int:envio_id>/', views.registrar_entrega, name='registrar_entrega'),  # Registrar nueva entrega
    path('entregas/<int:entrega_id>/', views.ver_entrega, name='ver_entrega'),  # Ver detalles de una entrega
    path('entregas/<int:entrega_id>/editar/', views.editar_entrega, name='editar_entrega'),  # Editar una entrega
    path('entregas/<int:entrega_id>/eliminar/', views.eliminar_entrega, name='eliminar_entrega'),  # Eliminar una entrega

    # Rutas para historial
    path('envios/<int:envio_id>/historial/', views.historial_envio, name='historial_envio'),  # Ver historial de un envío
    path('envios/<int:envio_id>/historial/<int:evento_id>/', views.ver_evento_historial, name='ver_evento_historial'),

    # Rutas para incidentes
    path('envios/<int:envio_id>/incidentes/', views.registrar_incidente, name='registrar_incidente'),
    path('envios/<int:envio_id>/incidentes/<int:incidente_id>/', views.ver_incidente, name='ver_incidente'),
    path('envios/<int:envio_id>/incidentes/<int:incidente_id>/editar/', views.editar_incidente, name='editar_incidente'),
    path('envios/<int:envio_id>/incidentes/<int:incidente_id>/eliminar/', views.eliminar_incidente, name='eliminar_incidente'),

    # API JSON endpoints
    path('entregas-json/', views.entregas_api_json, name='entregas_api_json'),
    path('envios-pendientes-json/', views.envios_pendientes_json, name='envios_pendientes_json'),
]
