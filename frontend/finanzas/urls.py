"""
URLs para la app finanzas con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    # Dashboard de contabilidad
    path('', views.list_transacciones, name='list'),
    path('dashboard/', views.list_transacciones, name='dashboard'),

    # Descarga de informes
    path('reporte/descargar/', views.download_report, name='download_report'),

    # CRUD para admins
    path('crear/', views.create_transaccion, name='create'),
    path('editar/<int:pk>/', views.update_transaccion, name='edit'),
    path('eliminar/<int:pk>/', views.delete_transaccion, name='delete'),
]