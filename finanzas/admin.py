from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from users.utils import is_association_admin, has_association
from .models import Transaccion


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    """Admin para gestión de transacciones con filtrado por asociación"""

    # Campos mostrados en la lista
    list_display = [
        'fecha_transaccion', 'concepto', 'cantidad_colored',
        'tipo_display', 'entidad', 'evento', 'asociacion'
    ]

    # Campos de búsqueda
    search_fields = ['concepto', 'descripcion', 'entidad']

    # Filtros laterales
    list_filter = ['fecha_transaccion', 'fecha_vencimiento', 'evento']

    # Organización en fieldsets
    fieldsets = (
        ('Información financiera', {
            'fields': ('cantidad', 'concepto', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_transaccion', 'fecha_vencimiento')
        }),
        ('Relaciones', {
            'fields': ('evento', 'entidad'),
            'classes': ('collapse',)  # Sección colapsable
        }),
    )

    # Campos de solo lectura
    readonly_fields = []

    # Ordenamiento por defecto
    ordering = ['-fecha_transaccion']

    def cantidad_colored(self, obj):
        """Mostrar cantidad con color según tipo"""
        if obj.cantidad >= 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">+{:.2f}€</span>',
                obj.cantidad
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">{:.2f}€</span>',
                obj.cantidad
            )
    cantidad_colored.short_description = 'Cantidad'
    cantidad_colored.admin_order_field = 'cantidad'

    def tipo_display(self, obj):
        """Mostrar tipo de transacción con emoji"""
        if obj.cantidad >= 0:
            return "💰 Ingreso"
        else:
            return "💸 Gasto"
    tipo_display.short_description = 'Tipo'

    def get_queryset(self, request):
        """Filtrar transacciones por asociación del usuario"""
        qs = super().get_queryset(request)
        if not has_association(request.user):
            return qs.none()
        return qs.filter(asociacion=request.user.profile.asociacion)

    def save_model(self, request, obj, form, change):
        """Auto-asignar asociación al crear nueva transacción"""
        if not has_association(request.user):
            raise PermissionDenied("Usuario sin asociación no puede crear transacciones")

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
