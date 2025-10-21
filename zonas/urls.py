from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_zonas, name='lista_zonas'),
    path('crear/', views.crear_zona, name='crear_zona'),
    path('<int:zona_id>/', views.ver_zona, name='ver_zona'),
    path('<int:zona_id>/editar/', views.editar_zona, name='editar_zona'),
    path('<int:zona_id>/eliminar/', views.eliminar_zona, name='eliminar_zona'),
]
