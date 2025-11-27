from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from users.utils import is_association_admin, has_association
from .models import Evento, Lugar


@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'ciudad', 'cp', 'asociacion')
    search_fields = ('nombre', 'direccion', 'ciudad')
    list_filter = ('ciudad', 'asociacion')


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """Admin para gestión de eventos con filtrado por asociación"""

    # Campos mostrados en la lista
    list_display = [
        'nombre', 'fecha_formatted', 'lugar_nombre', 'proyecto', 'asociacion'
    ]

    # Campos de búsqueda
    search_fields = ['nombre', 'descripcion', 'lugar_nombre', 'lugar_direccion', 'colaboradores']

    # Filtros laterales
    list_filter = ['fecha', 'proyecto']

    # Campos editables desde la lista
    list_editable = []

    # Organización en fieldsets
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'responsable', 'proyecto', 'descripcion', 'lugar_nombre', 'lugar_direccion')
        }),
        ('Fechas y duración', {
            'fields': ('fecha', 'duracion')
        }),
        ('Colaboradores y evaluación', {
            'fields': ('colaboradores', 'observaciones'),
            'description': 'Colaboradores y observaciones del evento'
        }),
    )

    # Campos de solo lectura
    readonly_fields = []

    # Ordenamiento por defecto
    ordering = ['-fecha']

    def fecha_formatted(self, obj):
        """Mostrar fecha formateada"""
        return obj.fecha.strftime('%d/%m/%Y %H:%M')
    fecha_formatted.short_description = 'Fecha'
    fecha_formatted.admin_order_field = 'fecha'

    def get_queryset(self, request):
        """Filtrar eventos por asociación del usuario"""
        qs = super().get_queryset(request)
        if not has_association(request.user):
            return qs.none()
        return qs.filter(asociacion=request.user.profile.asociacion)

    def save_model(self, request, obj, form, change):
        """Auto-asignar asociación al crear nuevo evento"""
        if not has_association(request.user):
            raise PermissionDenied("Usuario sin asociación no puede crear eventos")

        if not change:
            obj.asociacion = request.user.profile.asociacion
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """Solo admins de asociación pueden añadir"""
        return is_association_admin(request.user)

    def has_change_permission(self, request, obj=None):
        """Solo admins de asociación pueden editar"""
        if obj and has_association(request.user):
            return (is_association_admin(request.user) and
                   obj.asociacion == request.user.profile.asociacion)
        return is_association_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        """Solo admins de asociación pueden eliminar"""
        if obj and has_association(request.user):
            return (is_association_admin(request.user) and
                   obj.asociacion == request.user.profile.asociacion)
        return is_association_admin(request.user)
