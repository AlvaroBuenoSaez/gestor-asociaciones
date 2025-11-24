"""
Mixins para vistas con filtrado por asociación
"""
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from users.utils import has_association, is_association_admin


class AssociationFilterMixin:
    """Mixin para filtrar objetos por asociación del usuario"""

    def get_queryset(self):
        queryset = super().get_queryset()
        if not has_association(self.request.user):
            return queryset.none()
        return queryset.filter(asociacion=self.request.user.profile.asociacion)


class AssociationRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario tenga asociación"""

    def dispatch(self, request, *args, **kwargs):
        if not has_association(request.user):
            raise PermissionDenied("Usuario debe tener una asociación asignada")
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(AssociationRequiredMixin):
    """Mixin que requiere que el usuario sea admin de asociación"""

    def dispatch(self, request, *args, **kwargs):
        if not is_association_admin(request.user):
            raise PermissionDenied("Solo administradores pueden realizar esta acción")
        return super().dispatch(request, *args, **kwargs)


class AutoAssignAssociationMixin:
    """Mixin para auto-asignar asociación al crear objetos"""

    def form_valid(self, form):
        if not has_association(self.request.user):
            raise PermissionDenied("Usuario sin asociación no puede crear objetos")
        form.instance.asociacion = self.request.user.profile.asociacion
        return super().form_valid(form)