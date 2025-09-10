from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_zonas, name='lista_zonas'),  # Ruta para la lista de zonas
    path('crear/', views.crear_zona, name='crear_zona'),  # Ruta para crear una nueva zona
    path('<int:zona_id>/', views.ver_zona, name='ver_zona'),  # Ruta para ver los detalles de una zona
]
