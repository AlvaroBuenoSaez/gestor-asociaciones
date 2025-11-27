from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from users.utils import is_association_admin
from core.mixins import AssociationRequiredMixin, AssociationFilterMixin, AdminRequiredMixin, AutoAssignAssociationMixin
from .models import Entidad, Persona, Material
from eventos.models import Lugar
from .forms import EntidadForm, PersonaForm, LugarForm, MaterialForm

# --- Dashboard ---
class EntidadesDashboardView(AssociationRequiredMixin, TemplateView):
    template_name = 'entidades/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        asociacion = self.request.user.profile.asociacion

        context['total_entidades'] = Entidad.objects.filter(asociacion=asociacion).count()
        context['total_personas'] = Persona.objects.filter(asociacion=asociacion).count()
        context['total_lugares'] = Lugar.objects.filter(asociacion=asociacion).count()
        context['total_materiales'] = Material.objects.filter(asociacion=asociacion).count()

        # Últimos registros
        context['last_entidades'] = Entidad.objects.filter(asociacion=asociacion).order_by('-created_at')[:5]
        context['last_personas'] = Persona.objects.filter(asociacion=asociacion).order_by('-created_at')[:5]
        context['last_materiales'] = Material.objects.filter(asociacion=asociacion).order_by('-created_at')[:5]

        return context

# --- Entidades ---
class EntidadListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    model = Entidad
    template_name = 'entidades/entidad_list.html'
    context_object_name = 'entidades'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['active_tab'] = 'entidades'
        context['is_admin'] = is_association_admin(self.request.user)
        return context

class EntidadCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    model = Entidad
    form_class = EntidadForm
    template_name = 'entidades/entidad_form.html'
    success_url = reverse_lazy('entidades:entidad_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = 'Nueva Entidad'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Entidad "{form.instance.nombre}" creada.')
        return super().form_valid(form)

class EntidadUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    model = Entidad
    form_class = EntidadForm
    template_name = 'entidades/entidad_form.html'
    success_url = reverse_lazy('entidades:entidad_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = f'Editar: {self.object.nombre}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Entidad "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)

class EntidadDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    model = Entidad
    template_name = 'entidades/entidad_confirm_delete.html'
    success_url = reverse_lazy('entidades:entidad_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Entidad eliminada correctamente.')
        return super().delete(request, *args, **kwargs)

# --- Personas ---
class PersonaListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    model = Persona
    template_name = 'entidades/persona_list.html'
    context_object_name = 'personas'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['active_tab'] = 'personas'
        context['is_admin'] = is_association_admin(self.request.user)
        return context

class PersonaCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'entidades/persona_form.html'
    success_url = reverse_lazy('entidades:persona_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = 'Nueva Persona'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Persona "{form.instance.nombre}" creada.')
        return super().form_valid(form)

class PersonaUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'entidades/persona_form.html'
    success_url = reverse_lazy('entidades:persona_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = f'Editar: {self.object.nombre}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Persona "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)

class PersonaDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    model = Persona
    template_name = 'entidades/persona_confirm_delete.html'
    success_url = reverse_lazy('entidades:persona_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Persona eliminada correctamente.')
        return super().delete(request, *args, **kwargs)

# --- Lugares ---
class LugarListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    model = Lugar
    template_name = 'entidades/lugar_list.html'
    context_object_name = 'lugares'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['active_tab'] = 'lugares'
        context['is_admin'] = is_association_admin(self.request.user)
        return context

class LugarCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    model = Lugar
    form_class = LugarForm
    template_name = 'entidades/lugar_form.html'
    success_url = reverse_lazy('entidades:lugar_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = 'Nuevo Lugar'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Lugar "{form.instance.nombre}" creado.')
        return super().form_valid(form)

class LugarUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    model = Lugar
    form_class = LugarForm
    template_name = 'entidades/lugar_form.html'
    success_url = reverse_lazy('entidades:lugar_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = f'Editar: {self.object.nombre}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Lugar "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)

class LugarDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    model = Lugar
    template_name = 'entidades/lugar_confirm_delete.html'
    success_url = reverse_lazy('entidades:lugar_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lugar eliminado correctamente.')
        return super().delete(request, *args, **kwargs)

# --- Materiales ---
class MaterialListView(AssociationRequiredMixin, AssociationFilterMixin, ListView):
    model = Material
    template_name = 'entidades/material_list.html'
    context_object_name = 'materiales'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['active_tab'] = 'materiales'
        context['is_admin'] = is_association_admin(self.request.user)
        return context

class MaterialCreateView(AdminRequiredMixin, AutoAssignAssociationMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'entidades/material_form.html'
    success_url = reverse_lazy('entidades:material_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = 'Nuevo Material'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Material "{form.instance.nombre}" creado.')
        return super().form_valid(form)

class MaterialUpdateView(AdminRequiredMixin, AssociationFilterMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'entidades/material_form.html'
    success_url = reverse_lazy('entidades:material_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        context['title'] = f'Editar: {self.object.nombre}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Material "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)

class MaterialDeleteView(AdminRequiredMixin, AssociationFilterMixin, DeleteView):
    model = Material
    template_name = 'entidades/material_confirm_delete.html'
    success_url = reverse_lazy('entidades:material_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'entidades'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Material eliminado correctamente.')
        return super().delete(request, *args, **kwargs)
