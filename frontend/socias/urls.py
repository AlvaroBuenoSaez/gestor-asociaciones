"""
URLs para la app socias con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'socias'

urlpatterns = [
    # Lista de socias
    path('', views.list_socias, name='list'),

    # CRUD para admins
    path('crear/', views.create_socia, name='create'),
    path('editar/<int:pk>/', views.update_socia, name='edit'),
    path('eliminar/<int:pk>/', views.delete_socia, name='delete'),
]