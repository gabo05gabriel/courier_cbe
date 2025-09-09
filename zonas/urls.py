# zonas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_zonas, name='lista_zonas'),  # Lista de zonas
    # Otras rutas para zonas...
]
