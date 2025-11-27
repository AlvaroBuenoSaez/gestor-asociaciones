from django.contrib import admin
from .models import Proyecto


# @admin.register(Proyecto)
# class ProyectoAdmin(admin.ModelAdmin):
#     """Administración de proyectos"""
#     list_display = [
#         'nombre', 'responsable', 'estado_display', 'fecha_inicio',
#         'fecha_final', 'recursivo', 'asociacion'
#     ]
#     list_filter = [
#         'recursivo', 'fecha_inicio', 'fecha_final', 'asociacion'
#     ]
#     search_fields = [
#         'nombre', 'responsable', 'descripcion', 'involucrados'
#     ]
#     date_hierarchy = 'fecha_inicio'

#     fieldsets = (
#         ('Información Básica', {
#             'fields': ('asociacion', 'nombre', 'responsable')
#         }),
#         ('Detalles del Proyecto', {
#             'fields': ('descripcion', 'involucrados', 'materiales', 'lugar')
#         }),
#         ('Fechas y Configuración', {
#             'fields': ('fecha_inicio', 'fecha_final', 'recursivo')
#         }),
#     )

#     def get_queryset(self, request):
#         """Filtrar proyectos por asociación del usuario"""
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs

#         # Si el usuario tiene perfil y asociación, filtrar por ella
#         if hasattr(request.user, 'profile') and request.user.profile.asociacion:
#             return qs.filter(asociacion=request.user.profile.asociacion)

#         # Si no tiene asociación, no mostrar nada
#         return qs.none()
