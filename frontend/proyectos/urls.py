"""
URLs para la app proyectos con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    # Lista de proyectos
    path('', views.list_proyectos, name='list'),

    # CRUD para admins
    path('crear/', views.create_proyecto, name='create'),
    path('editar/<int:pk>/', views.update_proyecto, name='edit'),
    path('eliminar/<int:pk>/', views.delete_proyecto, name='delete'),
]