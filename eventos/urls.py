"""
URLs para la app eventos con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Lista de eventos/actividades
    path('', views.EventoListView.as_view(), name='list'),

    # CRUD para admins
    path('crear/', views.EventoCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', views.EventoUpdateView.as_view(), name='edit'),
    path('eliminar/<int:pk>/', views.EventoDeleteView.as_view(), name='delete'),

    # Mapas (funcionalidad separada)
    path('mapas/', views.mapas, name='mapas'),
]