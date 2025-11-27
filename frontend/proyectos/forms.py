from django import forms
from .models import Proyecto
from socias.models import Socia
from entidades.models import Persona, Material
from eventos.models import Lugar

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'nombre', 'responsable', 'descripcion',
            'socias_involucradas', 'personas_involucradas',
            'materiales_necesarios', 'lugar_fk',
            'fecha_inicio', 'fecha_final', 'recursivo'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_final': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'lugar_fk': forms.Select(attrs={'class': 'form-select'}),
            'recursivo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'socias_involucradas': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'personas_involucradas': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'materiales_necesarios': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)
        if self.asociacion:
            self.fields['responsable'].queryset = Socia.objects.filter(asociacion=self.asociacion)
            self.fields['socias_involucradas'].queryset = Socia.objects.filter(asociacion=self.asociacion)
            self.fields['personas_involucradas'].queryset = Persona.objects.filter(asociacion=self.asociacion)
            self.fields['materiales_necesarios'].queryset = Material.objects.filter(asociacion=self.asociacion)
            self.fields['lugar_fk'].queryset = Lugar.objects.filter(asociacion=self.asociacion)

