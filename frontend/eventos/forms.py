from django import forms
from .models import Evento
from datetime import datetime, timedelta

class EventoForm(forms.ModelForm):
    # Campos personalizados para fecha y hora
    fecha_dia = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha"
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'step': '300'}),
        label="Hora de inicio"
    )

    # Campos personalizados para duración
    duracion_cantidad = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2'}),
        label="Duración"
    )
    duracion_unidad = forms.ChoiceField(
        choices=[
            ('minutes', 'Minutos'),
            ('hours', 'Horas'),
            ('days', 'Días'),
            ('weeks', 'Semanas'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Unidad"
    )

    class Meta:
        model = Evento
        fields = [
            'nombre', 'responsable', 'proyecto', 'descripcion', 'lugar_nombre', 'lugar_direccion',
            'colaboradores', 'observaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'proyecto': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lugar_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Centro Cívico'}),
            'lugar_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
            'colaboradores': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)

        if self.asociacion:
            # Filtrar responsables (socias) por asociación
            from socias.models import Socia
            self.fields['responsable'].queryset = Socia.objects.filter(asociacion=self.asociacion)
            
            # Filtrar proyectos por asociación
            from proyectos.models import Proyecto
            self.fields['proyecto'].queryset = Proyecto.objects.filter(asociacion=self.asociacion)

        # Inicializar campos personalizados si hay instancia
        if self.instance:
            if self.instance.fecha:
                self.initial['fecha_dia'] = self.instance.fecha.date()
                self.initial['hora_inicio'] = self.instance.fecha.time()

            if self.instance.duracion:
                total_seconds = self.instance.duracion.total_seconds()
                if total_seconds % 604800 == 0: # Semanas
                    self.initial['duracion_cantidad'] = int(total_seconds / 604800)
                    self.initial['duracion_unidad'] = 'weeks'
                elif total_seconds % 86400 == 0: # Días
                    self.initial['duracion_cantidad'] = int(total_seconds / 86400)
                    self.initial['duracion_unidad'] = 'days'
                elif total_seconds % 3600 == 0: # Horas
                    self.initial['duracion_cantidad'] = int(total_seconds / 3600)
                    self.initial['duracion_unidad'] = 'hours'
                else: # Minutos
                    self.initial['duracion_cantidad'] = int(total_seconds / 60)
                    self.initial['duracion_unidad'] = 'minutes'

    def clean(self):
        cleaned_data = super().clean()
        fecha_dia = cleaned_data.get('fecha_dia')
        hora_inicio = cleaned_data.get('hora_inicio')

        if fecha_dia and hora_inicio:
            fecha = datetime.combine(fecha_dia, hora_inicio)
            cleaned_data['fecha'] = fecha
            # Asignar a la instancia para pasar la validación del modelo
            self.instance.fecha = fecha

        cantidad = cleaned_data.get('duracion_cantidad')
        unidad = cleaned_data.get('duracion_unidad')

        if cantidad and unidad:
            if unidad == 'minutes':
                cleaned_data['duracion'] = timedelta(minutes=cantidad)
            elif unidad == 'hours':
                cleaned_data['duracion'] = timedelta(hours=cantidad)
            elif unidad == 'days':
                cleaned_data['duracion'] = timedelta(days=cantidad)
            elif unidad == 'weeks':
                cleaned_data['duracion'] = timedelta(weeks=cantidad)
        else:
            cleaned_data['duracion'] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar valores calculados en clean()
        if 'fecha' in self.cleaned_data:
            instance.fecha = self.cleaned_data['fecha']
        
        if 'duracion' in self.cleaned_data:
            instance.duracion = self.cleaned_data['duracion']
            
        if commit:
            instance.save()
        return instance
