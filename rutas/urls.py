from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_rutas, name='lista_rutas'),  # Lista de rutas
    path("optimizar/<int:mensajero_id>/", views.optimizar_rutas, name="optimizar_rutas"),
    path('ver/<int:ruta_id>/', views.ver_ruta, name='ver_ruta'),  # Ver detalles de ruta
]
