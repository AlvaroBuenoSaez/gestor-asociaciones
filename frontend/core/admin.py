"""
Configuración del admin para la app core
"""
from django.contrib import admin
from .models import AsociacionVecinal


@admin.register(AsociacionVecinal)
class AsociacionVecinalAdmin(admin.ModelAdmin):
    """
    Configuración del admin para AsociacionVecinal
    """
    list_display = ('nombre', 'numero_registro', 'distrito', 'provincia', 'is_active', 'created_at')
    list_filter = ('is_active', 'provincia', 'distrito', 'created_at')
    search_fields = ('nombre', 'numero_registro', 'email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'numero_registro', 'descripcion')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'direccion')
        }),
        ('Ubicación', {
            'fields': ('distrito', 'provincia', 'codigo_postal')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return True
