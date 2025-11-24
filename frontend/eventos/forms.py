from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nombre', 'responsable', 'descripcion', 'lugar', 'fecha', 'duracion',
            'colaboradores', 'evaluacion', 'observaciones'
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'duracion': forms.TextInput(attrs={'class': 'form-control'}),
            'colaboradores': forms.TextInput(attrs={'class': 'form-control'}),
            'evaluacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)

        if self.asociacion:
            # Filtrar responsables (socias) por asociación
            # Esto requiere acceso a DB (Socia model)
            # Si queremos evitar DB, tendríamos que pasar las opciones desde la vista (obtenidas de API)
            # Por ahora, mantenemos el comportamiento híbrido (DB para forms)
            from socias.models import Socia
            self.fields['responsable'].queryset = Socia.objects.filter(asociacion=self.asociacion)
