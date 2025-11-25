"""
Vistas para gestión de finanzas/transacciones con CRUD completo
"""
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from users.utils import is_association_admin
from core.api import get_client
from core.mixins import (
    AssociationFilterMixin,
    AssociationRequiredMixin,
    AdminRequiredMixin,
    AutoAssignAssociationMixin
)
from .models import Transaccion
from .forms import TransaccionForm


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
    form_class = TransaccionForm
    template_name = 'contabilidad/create.html'
    success_url = reverse_lazy('finanzas:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'contabilidad'
        context['title'] = 'Nueva Transacción'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Handle file upload if present
        if 'comprobante' in self.request.FILES:
            uploaded_file = self.request.FILES['comprobante']
            client = get_client(self.request)

            try:
                files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}
                data = {
                    'asociacion_id': self.object.asociacion.id,
                    'transaction_id': self.object.id
                }

                api_response = client.post('drive/upload-transaction-file', data=data, files=files)

                if api_response and 'id' in api_response:
                    self.object.drive_file_id = api_response['id']
                    self.object.drive_file_name = api_response['name']
                    self.object.drive_file_link = api_response.get('webViewLink')
                    self.object.save()
                    messages.success(self.request, 'Comprobante subido a Google Drive correctamente.')
            except Exception as e:
                messages.warning(self.request, f'Transacción guardada, pero error al subir archivo: {str(e)}')

        tipo = "Ingreso" if form.instance.cantidad >= 0 else "Gasto"
        messages.success(self.request, f'{tipo} "{form.instance.concepto}" registrado exitosamente.')
        return response


class TransaccionUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    """Vista para editar transacción (solo admins)"""
    model = Transaccion
    form_class = TransaccionForm
    template_name = 'contabilidad/edit.html'
    success_url = reverse_lazy('finanzas:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'contabilidad'
        context['title'] = f'Editar: {self.object.concepto}'
        return context

    def form_valid(self, form):
        print("DEBUG: TransaccionUpdateView.form_valid called")
        response = super().form_valid(form)

        # Handle file upload if present
        if 'comprobante' in self.request.FILES:
            print(f"DEBUG: File found in request: {self.request.FILES['comprobante'].name}")
            uploaded_file = self.request.FILES['comprobante']
            client = get_client(self.request)

            try:
                files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}
                data = {
                    'asociacion_id': self.object.asociacion.id,
                    'transaction_id': self.object.id
                }
                print(f"DEBUG: Sending upload request to API for transaction {self.object.id}")

                api_response = client.post('drive/upload-transaction-file', data=data, files=files)
                print(f"DEBUG: API Response: {api_response}")

                if api_response and 'id' in api_response:
                    self.object.drive_file_id = api_response['id']
                    self.object.drive_file_name = api_response['name']
                    self.object.drive_file_link = api_response.get('webViewLink')
                    self.object.save()
                    messages.success(self.request, 'Comprobante subido a Google Drive correctamente.')
                else:
                    print("DEBUG: API response did not contain 'id'")
            except Exception as e:
                print(f"DEBUG: Exception during upload: {str(e)}")
                messages.warning(self.request, f'Transacción actualizada, pero error al subir archivo: {str(e)}')
        else:
            print("DEBUG: No 'comprobante' in request.FILES")

        messages.success(self.request, f'Transacción "{form.instance.concepto}" actualizada exitosamente.')
        return response

    def form_invalid(self, form):
        print(f"DEBUG: TransaccionUpdateView.form_invalid called. Errors: {form.errors}")
        return super().form_invalid(form)


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
