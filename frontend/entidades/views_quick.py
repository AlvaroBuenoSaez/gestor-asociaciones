from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import CreateView
from core.mixins import AssociationRequiredMixin, AutoAssignAssociationMixin
from .models import Persona, Material
from eventos.models import Lugar
from .forms import PersonaForm, MaterialForm, LugarForm

class QuickCreateBaseView(AssociationRequiredMixin, AutoAssignAssociationMixin, CreateView):
    template_name = 'entidades/quick_create_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Algunos forms necesitan 'asociacion' en kwargs
        if self.form_class in [PersonaForm, MaterialForm]:
            kwargs['asociacion'] = self.request.user.profile.asociacion
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.asociacion = self.request.user.profile.asociacion
        self.object.save()
        
        # Guardar M2M si existen
        form.save_m2m()

        return JsonResponse({
            'success': True,
            'id': self.object.id,
            'text': str(self.object),
            'type': self.model._meta.model_name
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'html': render_to_string(self.template_name, {'form': form}, request=self.request)
        })

class PersonaQuickCreateView(QuickCreateBaseView):
    model = Persona
    form_class = PersonaForm

class MaterialQuickCreateView(QuickCreateBaseView):
    model = Material
    form_class = MaterialForm

class LugarQuickCreateView(QuickCreateBaseView):
    model = Lugar
    form_class = LugarForm
