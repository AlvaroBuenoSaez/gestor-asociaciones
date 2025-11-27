from django.urls import path
from . import views
from . import views_quick

app_name = 'entidades'

urlpatterns = [
    path('', views.EntidadesDashboardView.as_view(), name='dashboard'),

    # Entidades
    path('entidades/', views.EntidadListView.as_view(), name='entidad_list'),
    path('entidades/crear/', views.EntidadCreateView.as_view(), name='entidad_create'),
    path('entidades/editar/<int:pk>/', views.EntidadUpdateView.as_view(), name='entidad_update'),
    path('entidades/eliminar/<int:pk>/', views.EntidadDeleteView.as_view(), name='entidad_delete'),

    # Personas
    path('personas/', views.PersonaListView.as_view(), name='persona_list'),
    path('personas/crear/', views.PersonaCreateView.as_view(), name='persona_create'),
    path('personas/editar/<int:pk>/', views.PersonaUpdateView.as_view(), name='persona_update'),
    path('personas/eliminar/<int:pk>/', views.PersonaDeleteView.as_view(), name='persona_delete'),

    # Lugares
    path('lugares/', views.LugarListView.as_view(), name='lugar_list'),
    path('lugares/crear/', views.LugarCreateView.as_view(), name='lugar_create'),
    path('lugares/editar/<int:pk>/', views.LugarUpdateView.as_view(), name='lugar_update'),
    path('lugares/eliminar/<int:pk>/', views.LugarDeleteView.as_view(), name='lugar_delete'),

    # Materiales
    path('materiales/', views.MaterialListView.as_view(), name='material_list'),
    path('materiales/crear/', views.MaterialCreateView.as_view(), name='material_create'),
    path('materiales/editar/<int:pk>/', views.MaterialUpdateView.as_view(), name='material_update'),
    path('materiales/eliminar/<int:pk>/', views.MaterialDeleteView.as_view(), name='material_delete'),

    # Quick Create (AJAX)
    path('quick/persona/', views_quick.PersonaQuickCreateView.as_view(), name='quick_persona_create'),
    path('quick/material/', views_quick.MaterialQuickCreateView.as_view(), name='quick_material_create'),
    path('quick/lugar/', views_quick.LugarQuickCreateView.as_view(), name='quick_lugar_create'),
]
