from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from users.utils import is_association_admin, has_association
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """Admin para gestión de eventos con filtrado por asociación"""

    # Campos mostrados en la lista
    list_display = [
        'nombre', 'fecha_formatted', 'lugar',
        'evaluacion', 'evaluacion_stars', 'asociacion'
    ]

    # Campos de búsqueda
    search_fields = ['nombre', 'descripcion', 'lugar', 'colaboradores']

    # Filtros laterales
    list_filter = ['fecha', 'evaluacion']

    # Campos editables desde la lista
    list_editable = ['evaluacion']

    # Organización en fieldsets
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'responsable', 'descripcion', 'lugar')
        }),
        ('Fechas y duración', {
            'fields': ('fecha', 'duracion')
        }),
        ('Colaboradores y evaluación', {
            'fields': ('colaboradores', 'evaluacion', 'observaciones'),
            'description': 'Colaboradores y evaluación del evento (1-5 estrellas)'
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

    def evaluacion_stars(self, obj):
        """Mostrar evaluación con estrellas"""
        if obj.evaluacion:
            stars = '⭐' * obj.evaluacion
            return format_html('<span title="{}/5">{}</span>', obj.evaluacion, stars)
        return '❌ Sin evaluar'
    evaluacion_stars.short_description = 'Evaluación'
    evaluacion_stars.admin_order_field = 'evaluacion'

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
