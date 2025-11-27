"""
URLs para la app eventos con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Lista de eventos/actividades
    path('', views.list_eventos, name='list'),

    # CRUD para admins
    path('crear/', views.create_evento, name='create'),
    path('editar/<int:pk>/', views.update_evento, name='edit'),
    path('eliminar/<int:pk>/', views.delete_evento, name='delete'),

    # Mapas (funcionalidad separada)
    path('mapas/', views.mapas, name='mapas'),

    # API Proxy
    path('api/lugares/buscar/', views.search_lugares, name='search_lugares'),
]