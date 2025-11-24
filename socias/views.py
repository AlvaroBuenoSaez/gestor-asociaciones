"""
Vistas para gestión de socias con CRUD completo
"""
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from users.utils import is_association_admin
from core.mixins import (
    AssociationFilterMixin,
    AssociationRequiredMixin,
    AdminRequiredMixin,
    AutoAssignAssociationMixin
)
from .models import Socia
from .forms import SociaForm


class SociaListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    """Vista para listar socias de la asociación con búsqueda y filtrado"""
    model = Socia
    template_name = 'socias/list.html'
    context_object_name = 'socias'
    paginate_by = 20

    def get_queryset(self):
        """Aplicar filtros de búsqueda y filtrado"""
        queryset = super().get_queryset()

        # Búsqueda general
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(numero_socia__icontains=search) |
                Q(nombre__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(telefono__icontains=search) |
                Q(direccion__icontains=search) |
                Q(provincia__icontains=search) |
                Q(codigo_postal__icontains=search)
            )

        # Filtro por estado de pago
        pagado = self.request.GET.get('pagado')
        if pagado == 'si':
            queryset = queryset.filter(pagado=True)
        elif pagado == 'no':
            queryset = queryset.filter(pagado=False)

        # Filtro por provincia
        provincia = self.request.GET.get('provincia')
        if provincia:
            queryset = queryset.filter(provincia__icontains=provincia)

        # Ordenamiento
        sort = self.request.GET.get('sort', 'numero_socia')
        if sort in ['numero_socia', 'nombre', 'apellidos', 'fecha_inscripcion', '-numero_socia', '-nombre', '-apellidos', '-fecha_inscripcion']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'socias'
        context['asociacion'] = self.request.user.profile.asociacion
        context['is_admin'] = is_association_admin(self.request.user)

        # Parámetros de búsqueda actuales
        context['current_search'] = self.request.GET.get('search', '')
        context['current_pagado'] = self.request.GET.get('pagado', '')
        context['current_provincia'] = self.request.GET.get('provincia', '')
        context['current_sort'] = self.request.GET.get('sort', 'numero_socia')

        # Estadísticas basadas en el queryset filtrado
        all_socias = self.get_queryset()
        context['total_socias'] = all_socias.count()
        context['socias_pagadas'] = all_socias.filter(pagado=True).count()
        context['socias_pendientes'] = all_socias.filter(pagado=False).count()

        # Lista de provincias para el filtro
        context['provincias_disponibles'] = Socia.objects.filter(
            asociacion=self.request.user.profile.asociacion
        ).exclude(
            provincia__isnull=True
        ).exclude(
            provincia__exact=''
        ).values_list('provincia', flat=True).distinct().order_by('provincia')

        return context


class SociaCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    """Vista para crear nueva socia (solo admins)"""
    model = Socia
    form_class = SociaForm
    template_name = 'socias/create.html'
    success_url = reverse_lazy('socias:list')

    def get_form_kwargs(self):
        """Pasar la asociación del usuario al formulario"""
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'profile') and self.request.user.profile.asociacion:
            kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'socias'
        context['title'] = 'Nueva Socia'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Socia "{form.instance.nombre} {form.instance.apellidos}" creada exitosamente.')
        return super().form_valid(form)


class SociaUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    """Vista para editar socia (solo admins)"""
    model = Socia
    form_class = SociaForm
    template_name = 'socias/edit.html'
    success_url = reverse_lazy('socias:list')

    def get_form_kwargs(self):
        """Pasar la asociación del usuario al formulario"""
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'profile') and self.request.user.profile.asociacion:
            kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'socias'
        context['title'] = f'Editar Socia: {self.object.nombre}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Socia "{form.instance.nombre} {form.instance.apellidos}" actualizada exitosamente.')
        return super().form_valid(form)


class SociaDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    """Vista para eliminar socia (solo admins)"""
    model = Socia
    template_name = 'socias/delete.html'
    success_url = reverse_lazy('socias:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'socias'
        context['title'] = f'Eliminar Socia: {self.object.nombre}'
        return context

    def delete(self, request, *args, **kwargs):
        socia = self.get_object()
        messages.success(request, f'Socia "{socia.nombre} {socia.apellidos}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
