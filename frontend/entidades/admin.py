from django.contrib import admin
from .models import Entidad, Persona, Material
from eventos.models import Lugar

@admin.register(Entidad)
class EntidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'telefono', 'email', 'asociacion')
    search_fields = ('nombre', 'tipo')
    list_filter = ('tipo', 'asociacion')

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'cargo', 'entidad', 'telefono', 'asociacion', 'proyecto')
    search_fields = ('nombre', 'apellidos', 'cargo')
    list_filter = ('entidad', 'asociacion', 'proyecto')
    filter_horizontal = ('le_conoce',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'lugar', 'asociacion')
    search_fields = ('nombre', 'uso')
    list_filter = ('asociacion', 'lugar')

# Lugar is imported from eventos, so it might be registered there.
# But if we want to manage it here too or if it wasn't registered:
# admin.site.register(Lugar) # It's likely registered in events/admin.py

