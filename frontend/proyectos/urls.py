"""
URLs para la app proyectos con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    # Lista de proyectos
    path('', views.ProyectoListView.as_view(), name='list'),

    # CRUD para admins
    path('crear/', views.ProyectoCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', views.ProyectoUpdateView.as_view(), name='edit'),
    path('eliminar/<int:pk>/', views.ProyectoDeleteView.as_view(), name='delete'),
]