"""
Vistas para gestión de proyectos con CRUD completo
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
from .models import Proyecto
from .forms import ProyectoForm


class ProyectoListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    """Vista para listar proyectos de la asociación con búsqueda y filtros"""
    model = Proyecto
    template_name = 'proyectos/list.html'
    context_object_name = 'proyectos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        estado = self.request.GET.get('estado', '')
        recursivo = self.request.GET.get('recursivo', '')
        order = self.request.GET.get('order', '-fecha_inicio')

        # Filtrar por búsqueda (nombre, descripción, responsable, lugar)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(responsable__icontains=search) |
                Q(lugar__icontains=search) |
                Q(involucrados__icontains=search) |
                Q(materiales__icontains=search)
            )

        # Filtrar por estado (usando lógica manual ya que es una propiedad calculada)
        if estado:
            from django.utils import timezone
            hoy = timezone.now().date()

            if estado == 'pendiente':
                queryset = queryset.filter(fecha_inicio__gt=hoy)
            elif estado == 'finalizado':
                queryset = queryset.filter(fecha_final__lt=hoy, fecha_final__isnull=False)
            elif estado == 'en_curso':
                queryset = queryset.filter(
                    Q(fecha_inicio__lte=hoy) &
                    (Q(fecha_final__gte=hoy) | Q(fecha_final__isnull=True))
                )

        # Filtrar por recursivo
        if recursivo == 'si':
            queryset = queryset.filter(recursivo=True)
        elif recursivo == 'no':
            queryset = queryset.filter(recursivo=False)

        # Ordenar
        order_mapping = {
            'fecha_inicio': 'fecha_inicio',
            '-fecha_inicio': '-fecha_inicio',
            'fecha_final': 'fecha_final',
            '-fecha_final': '-fecha_final',
            'nombre': 'nombre',
            '-nombre': '-nombre'
        }

        if order in order_mapping:
            queryset = queryset.order_by(order_mapping[order])
        else:
            queryset = queryset.order_by('-fecha_inicio')  # Por defecto: más recientes primero

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'proyectos'

        # Obtener asociación del usuario de forma segura
        try:
            if self.request.user.is_authenticated:
                context['asociacion'] = self.request.user.profile.asociacion  # type: ignore
        except AttributeError:
            pass

        context['is_admin'] = is_association_admin(self.request.user)

        # Parámetros de búsqueda actuales
        context['current_search'] = self.request.GET.get('search', '')
        context['current_estado'] = self.request.GET.get('estado', '')
        context['current_recursivo'] = self.request.GET.get('recursivo', '')
        context['current_order'] = self.request.GET.get('order', '-fecha_inicio')

        # Obtener todos los proyectos de la asociación para estadísticas
        all_proyectos = super().get_queryset()
        filtered_proyectos = self.get_queryset()

        # Estadísticas generales (calculadas manualmente ya que estado es una propiedad)
        total_proyectos = all_proyectos.count()

        # Calcular estadísticas por estado usando lógica manual
        from django.utils import timezone
        hoy = timezone.now().date()

        pendientes = 0
        en_curso = 0
        finalizados = 0
        recursivos = all_proyectos.filter(recursivo=True).count()

        for proyecto in all_proyectos:
            if hoy < proyecto.fecha_inicio:
                pendientes += 1
            elif proyecto.fecha_final and hoy > proyecto.fecha_final:
                finalizados += 1
            else:
                en_curso += 1

        # Estadísticas filtradas
        filtered_count = filtered_proyectos.count()

        context.update({
            'total_proyectos': total_proyectos,
            'proyectos_pendientes': pendientes,
            'proyectos_en_curso': en_curso,
            'proyectos_finalizados': finalizados,
            'proyectos_recursivos': recursivos,
            'filtered_count': filtered_count,
        })

        # Opciones para filtros
        estados_choices = [
            ('pendiente', 'Pendiente'),
            ('en_curso', 'En Curso'),
            ('finalizado', 'Finalizado')
        ]
        context['estados'] = estados_choices
        context['recursivo_choices'] = [('si', 'Sí'), ('no', 'No')]

        return context


class ProyectoCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    """Vista para crear nuevo proyecto (solo admins)"""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/create.html'
    success_url = reverse_lazy('proyectos:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
             kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'proyectos'
        context['title'] = 'Nuevo Proyecto'

        # Obtener asociación del usuario de forma segura
        try:
            if self.request.user.is_authenticated:
                context['asociacion'] = self.request.user.profile.asociacion  # type: ignore
        except AttributeError:
            pass

        context['is_admin'] = is_association_admin(self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Proyecto "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)


class ProyectoUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    """Vista para editar proyecto (solo admins)"""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/edit.html'
    success_url = reverse_lazy('proyectos:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
             kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'proyectos'
        context['title'] = f'Editar: {self.get_object().nombre}'  # type: ignore

        # Obtener asociación del usuario de forma segura
        try:
            if self.request.user.is_authenticated:
                context['asociacion'] = self.request.user.profile.asociacion  # type: ignore
        except AttributeError:
            pass

        context['is_admin'] = is_association_admin(self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Proyecto "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)


class ProyectoDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    """Vista para eliminar proyecto (solo admins)"""
    model = Proyecto
    template_name = 'proyectos/delete.html'
    success_url = reverse_lazy('proyectos:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'proyectos'
        context['title'] = f'Eliminar: {self.get_object().nombre}'  # type: ignore

        # Obtener asociación del usuario de forma segura
        try:
            if self.request.user.is_authenticated:
                context['asociacion'] = self.request.user.profile.asociacion  # type: ignore
        except AttributeError:
            pass

        context['is_admin'] = is_association_admin(self.request.user)
        return context

    def delete(self, request, *args, **kwargs):
        proyecto = self.get_object()
        messages.success(request, f'Proyecto "{proyecto.nombre}" eliminado exitosamente.')  # type: ignore
        return super().delete(request, *args, **kwargs)
