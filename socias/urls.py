"""
URLs para la app socias con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'socias'

urlpatterns = [
    # Lista de socias
    path('', views.SociaListView.as_view(), name='list'),

    # CRUD para admins
    path('crear/', views.SociaCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', views.SociaUpdateView.as_view(), name='edit'),
    path('eliminar/<int:pk>/', views.SociaDeleteView.as_view(), name='delete'),
]