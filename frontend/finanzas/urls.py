"""
URLs para la app finanzas con CRUD completo
"""
from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    # Dashboard de contabilidad
    path('', views.TransaccionListView.as_view(), name='list'),
    path('dashboard/', views.TransaccionListView.as_view(), name='dashboard'),
    
    # Descarga de informes
    path('reporte/descargar/', views.DownloadReportView.as_view(), name='download_report'),

    # CRUD para admins
    path('crear/', views.TransaccionCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', views.TransaccionUpdateView.as_view(), name='edit'),
    path('eliminar/<int:pk>/', views.TransaccionDeleteView.as_view(), name='delete'),
]