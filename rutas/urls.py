# rutas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_rutas, name='lista_rutas'),  # Lista de rutas
    # Otras rutas relacionadas con rutas...
]
