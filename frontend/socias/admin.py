from django.contrib import admin
from django.core.exceptions import PermissionDenied
from users.utils import is_association_admin, has_association
from .models import Socia


# @admin.register(Socia)
# class SociaAdmin(admin.ModelAdmin):
#     """Admin para gestión de socias con filtrado por asociación"""

#     # Campos mostrados en la lista
#     list_display = [
#         'numero_socia', 'nombre', 'apellidos', 'telefono',
#         'pagado', 'fecha_inscripcion', 'asociacion'
#     ]

#     # Campos de búsqueda
#     search_fields = ['numero_socia', 'nombre', 'apellidos', 'telefono']

#     # Filtros laterales
#     list_filter = ['pagado', 'fecha_inscripcion', 'provincia']

#     # Campos editables desde la lista
#     list_editable = ['pagado']

#     # Organización en fieldsets
#     fieldsets = (
#         ('Información básica', {
#             'fields': ('numero_socia', 'nombre', 'apellidos')
#         }),
#         ('Contacto', {
#             'fields': ('telefono', 'direccion', 'provincia', 'codigo_postal', 'pais')
#         }),
#         ('Fechas', {
#             'fields': ('nacimiento', 'fecha_inscripcion')
#         }),
#         ('Estado', {
#             'fields': ('pagado', 'descripcion')
#         }),
#     )

#     # Campos de solo lectura
#     readonly_fields = ['fecha_inscripcion']

#     def get_queryset(self, request):
#         """Filtrar socias por asociación del usuario"""
#         qs = super().get_queryset(request)
#         if not has_association(request.user):
#             return qs.none()  # Sin asociación = sin datos
#         return qs.filter(asociacion=request.user.profile.asociacion)

#     def save_model(self, request, obj, form, change):
#         """Auto-asignar asociación al crear nueva socia"""
#         if not has_association(request.user):
#             raise PermissionDenied("Usuario sin asociación no puede crear socias")

#         if not change:  # Solo al crear (no al editar)
#             obj.asociacion = request.user.profile.asociacion
#         super().save_model(request, obj, form, change)

#     def has_add_permission(self, request):
#         """Solo admins de asociación pueden añadir"""
#         return is_association_admin(request.user)

#     def has_change_permission(self, request, obj=None):
#         """Solo admins de asociación pueden editar"""
#         if obj and has_association(request.user):
#             # Verificar que el objeto pertenece a su asociación
#             return (is_association_admin(request.user) and
#                    obj.asociacion == request.user.profile.asociacion)
#         return is_association_admin(request.user)

#     def has_delete_permission(self, request, obj=None):
#         """Solo admins de asociación pueden eliminar"""
#         if obj and has_association(request.user):
#             return (is_association_admin(request.user) and
#                    obj.asociacion == request.user.profile.asociacion)
#         return is_association_admin(request.user)
