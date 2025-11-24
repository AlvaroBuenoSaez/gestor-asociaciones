"""
Vistas para gestión de finanzas/transacciones con CRUD completo
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
from .models import Transaccion


class TransaccionListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    """Vista para listar transacciones de la asociación con búsqueda y filtros"""
    model = Transaccion
    template_name = 'contabilidad/list.html'
    context_object_name = 'transacciones'
    paginate_by = 20

    def get_queryset(self):
        """Aplicar filtros de búsqueda y ordenamiento"""
        queryset = super().get_queryset().order_by('-fecha_transaccion')

        # Filtro de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(concepto__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(entidad__icontains=search)
            )

        # Filtro por tipo (ingreso/gasto)
        tipo = self.request.GET.get('tipo')
        if tipo == 'ingreso':
            queryset = queryset.filter(cantidad__gt=0)
        elif tipo == 'gasto':
            queryset = queryset.filter(cantidad__lt=0)

        # Filtro por entidad
        entidad = self.request.GET.get('entidad')
        if entidad:
            queryset = queryset.filter(entidad__icontains=entidad)

        # Filtro por año
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(fecha_transaccion__year=year)

        # Ordenamiento
        sort = self.request.GET.get('sort', '-fecha_transaccion')
        if sort:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'contabilidad'
        context['asociacion'] = self.request.user.profile.asociacion
        context['is_admin'] = is_association_admin(self.request.user)

        # Parámetros de búsqueda actuales
        context['current_search'] = self.request.GET.get('search', '')
        context['current_tipo'] = self.request.GET.get('tipo', '')
        context['current_entidad'] = self.request.GET.get('entidad', '')
        context['current_year'] = self.request.GET.get('year', '')
        context['current_sort'] = self.request.GET.get('sort', '-fecha_transaccion')

        # Estadísticas financieras (de todas las transacciones, no solo las filtradas)
        todas_transacciones = Transaccion.objects.filter(asociacion=self.request.user.profile.asociacion)
        transacciones_filtradas = self.get_queryset()

        # Stats generales
        total_ingresos = sum(t.cantidad for t in todas_transacciones if t.cantidad > 0)
        total_gastos = sum(abs(t.cantidad) for t in todas_transacciones if t.cantidad < 0)
        balance = total_ingresos - total_gastos

        # Stats filtradas
        ingresos_filtrados = sum(t.cantidad for t in transacciones_filtradas if t.cantidad > 0)
        gastos_filtrados = sum(abs(t.cantidad) for t in transacciones_filtradas if t.cantidad < 0)

        context.update({
            'total_transacciones': transacciones_filtradas.count(),
            'total_ingresos': total_ingresos,
            'total_gastos': total_gastos,
            'balance': balance,
            'ingresos_filtrados': ingresos_filtrados,
            'gastos_filtrados': gastos_filtrados,
        })

        # Obtener años disponibles y entidades para filtros
        context['years_disponibles'] = sorted(
            set(t.fecha_transaccion.year for t in todas_transacciones if t.fecha_transaccion),
            reverse=True
        )
        context['entidades_disponibles'] = sorted(
            set(t.entidad for t in todas_transacciones if t.entidad and t.entidad.strip())
        )

        return context


class TransaccionCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    """Vista para crear nueva transacción (solo admins)"""
    model = Transaccion
    template_name = 'contabilidad/create.html'
    fields = [
        'cantidad', 'concepto', 'descripcion',
        'fecha_transaccion', 'fecha_vencimiento',
        'evento', 'entidad'
    ]
    success_url = reverse_lazy('finanzas:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'contabilidad'
        context['title'] = 'Nueva Transacción'
        return context

    def form_valid(self, form):
        tipo = "Ingreso" if form.instance.cantidad >= 0 else "Gasto"
        messages.success(self.request, f'{tipo} "{form.instance.concepto}" registrado exitosamente.')
        return super().form_valid(form)


class TransaccionUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    """Vista para editar transacción (solo admins)"""
    model = Transaccion
    template_name = 'contabilidad/edit.html'
    fields = [
        'cantidad', 'concepto', 'descripcion',
        'fecha_transaccion', 'fecha_vencimiento',
        'evento', 'entidad'
    ]
    success_url = reverse_lazy('finanzas:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'contabilidad'
        context['title'] = f'Editar: {self.object.concepto}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Transacción "{form.instance.concepto}" actualizada exitosamente.')
        return super().form_valid(form)


class TransaccionDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    """Vista para eliminar transacción (solo admins)"""
    model = Transaccion
    template_name = 'contabilidad/delete.html'
    success_url = reverse_lazy('finanzas:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'contabilidad'
        context['title'] = f'Eliminar: {self.object.concepto}'
        return context

    def delete(self, request, *args, **kwargs):
        transaccion = self.get_object()
        messages.success(request, f'Transacción "{transaccion.concepto}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
