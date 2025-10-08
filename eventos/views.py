"""
Vistas para gestión de eventos y actividades con CRUD completo
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from users.utils import association_required, is_association_admin
from core.mixins import (
    AssociationFilterMixin,
    AssociationRequiredMixin,
    AdminRequiredMixin,
    AutoAssignAssociationMixin
)
from .models import Evento


class EventoListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    """Vista para listar eventos de la asociación con búsqueda y filtros"""
    model = Evento
    template_name = 'actividades/list.html'
    context_object_name = 'eventos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        year = self.request.GET.get('year', '')
        order = self.request.GET.get('order', 'fecha')

        # Filtrar por búsqueda (nombre, descripción, lugar)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(lugar__icontains=search) |
                Q(colaboradores__icontains=search)
            )

        # Filtrar por año
        if year:
            queryset = queryset.filter(fecha__year=year)

        # Ordenar
        order_mapping = {
            'fecha': 'fecha',
            '-fecha': '-fecha',
            'nombre': 'nombre',
            '-nombre': '-nombre',
            'participantes': 'participantes',
            '-participantes': '-participantes',
            'evaluacion': 'evaluacion',
            '-evaluacion': '-evaluacion'
        }

        if order in order_mapping:
            queryset = queryset.order_by(order_mapping[order])
        else:
            queryset = queryset.order_by('-fecha')  # Por defecto: más recientes primero

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'actividades'

        # Obtener asociación del usuario de forma segura
        try:
            if self.request.user.is_authenticated:
                context['asociacion'] = self.request.user.profile.asociacion  # type: ignore
        except AttributeError:
            pass

        context['is_admin'] = is_association_admin(self.request.user)

        # Parámetros de búsqueda actuales
        context['current_search'] = self.request.GET.get('search', '')
        context['current_year'] = self.request.GET.get('year', '')
        context['current_order'] = self.request.GET.get('order', 'fecha')

        # Obtener todos los eventos de la asociación para estadísticas
        all_eventos = super().get_queryset()
        filtered_eventos = self.get_queryset()

        # Estadísticas generales
        total_eventos = all_eventos.count()
        eventos_evaluados = all_eventos.exclude(evaluacion__isnull=True).count()
        promedio_evaluacion = 0
        if eventos_evaluados > 0:
            suma_evaluaciones = sum(e.evaluacion for e in all_eventos if e.evaluacion)
            promedio_evaluacion = round(suma_evaluaciones / eventos_evaluados, 1)

        # Estadísticas filtradas
        filtered_count = filtered_eventos.count()

        context.update({
            'total_eventos': total_eventos,
            'eventos_evaluados': eventos_evaluados,
            'promedio_evaluacion': promedio_evaluacion,
            'filtered_count': filtered_count,
        })

        # Años disponibles para el filtro
        years = all_eventos.values_list('fecha__year', flat=True).distinct().order_by('-fecha__year')
        context['years'] = list(years)

        return context


class EventoCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    """Vista para crear nuevo evento (solo admins)"""
    model = Evento
    template_name = 'actividades/create.html'
    fields = [
        'nombre', 'responsable', 'descripcion', 'lugar', 'fecha', 'duracion',
        'colaboradores', 'evaluacion', 'observaciones'
    ]
    success_url = reverse_lazy('eventos:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar responsables solo a socias de la asociación del usuario
        try:
            if self.request.user.is_authenticated:
                asociacion = self.request.user.profile.asociacion  # type: ignore
                if 'responsable' in form.fields:
                    form.fields['responsable'].queryset = form.fields['responsable'].queryset.filter(asociacion=asociacion)  # type: ignore
        except AttributeError:
            pass
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'actividades'
        context['title'] = 'Nuevo Evento'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Evento "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)


class EventoUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    """Vista para editar evento (solo admins)"""
    model = Evento
    template_name = 'actividades/edit.html'
    fields = [
        'nombre', 'responsable', 'descripcion', 'lugar', 'fecha', 'duracion',
        'colaboradores', 'evaluacion', 'observaciones'
    ]
    success_url = reverse_lazy('eventos:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar responsables solo a socias de la asociación del usuario
        try:
            if self.request.user.is_authenticated:
                asociacion = self.request.user.profile.asociacion  # type: ignore
                if 'responsable' in form.fields:
                    form.fields['responsable'].queryset = form.fields['responsable'].queryset.filter(asociacion=asociacion)  # type: ignore
        except AttributeError:
            pass
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'actividades'
        context['title'] = f'Editar: {self.get_object().nombre}'  # type: ignore

        return context

    def form_valid(self, form):
        messages.success(self.request, f'Evento "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)


class EventoDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    """Vista para eliminar evento (solo admins)"""
    model = Evento
    template_name = 'actividades/delete.html'
    success_url = reverse_lazy('eventos:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'actividades'
        context['title'] = f'Eliminar: {self.get_object().nombre}'  # type: ignore
        return context

    def delete(self, request, *args, **kwargs):
        evento = self.get_object()
        messages.success(request, f'Evento "{evento.nombre}" eliminado exitosamente.')  # type: ignore
        return super().delete(request, *args, **kwargs)


@association_required
def mapas(request):
    """Vista de mapas del barrio"""
    context = {
        'section': 'mapas',
        'asociacion': request.user.profile.asociacion,  # type: ignore
    }
    return render(request, 'mapas/viewer.html', context)
