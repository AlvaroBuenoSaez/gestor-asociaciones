from django import forms
from .models import Entidad, Persona, Material
from eventos.models import Lugar
from socias.models import Socia
from proyectos.models import Proyecto
from finanzas.models import Transaccion

class EntidadForm(forms.ModelForm):
    class Meta:
        model = Entidad
        fields = ['nombre', 'tipo', 'descripcion', 'telefono', 'email', 'web', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ayuntamiento, Empresa...'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'web': forms.URLInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['nombre', 'apellidos', 'contacto', 'cargo', 'entidad', 'telefono', 'email', 'observaciones', 'proyecto', 'le_conoce']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Información de contacto adicional'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'entidad': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'le_conoce': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)
        if self.asociacion:
            self.fields['entidad'].queryset = Entidad.objects.filter(asociacion=self.asociacion)
            self.fields['proyecto'].queryset = Proyecto.objects.filter(asociacion=self.asociacion)
            self.fields['le_conoce'].queryset = Socia.objects.filter(asociacion=self.asociacion)

class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugar
        fields = ['nombre', 'direccion', 'numero', 'cp', 'ciudad', 'pais', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control geoapify-autocomplete-input', 'placeholder': 'Escribe para buscar dirección...'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'cp': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['nombre', 'uso', 'precio', 'transaccion_compra', 'lugar', 'encargado_persona', 'encargado_socia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'uso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transaccion_compra': forms.Select(attrs={'class': 'form-select'}),
            'lugar': forms.Select(attrs={'class': 'form-select'}),
            'encargado_persona': forms.Select(attrs={'class': 'form-select'}),
            'encargado_socia': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)
        if self.asociacion:
            self.fields['transaccion_compra'].queryset = Transaccion.objects.filter(asociacion=self.asociacion)
            self.fields['lugar'].queryset = Lugar.objects.filter(asociacion=self.asociacion)
            self.fields['encargado_persona'].queryset = Persona.objects.filter(asociacion=self.asociacion)
            self.fields['encargado_socia'].queryset = Socia.objects.filter(asociacion=self.asociacion)
