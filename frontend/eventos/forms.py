from django import forms
from .models import Evento, Lugar
from entidades.models import Persona, Material
from datetime import datetime, timedelta

class EventoForm(forms.ModelForm):
    # Campos personalizados para fecha y hora
    fecha_dia = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha"
    )

    # Selectores de hora y minutos
    hora = forms.ChoiceField(
        choices=[(str(h).zfill(2), str(h).zfill(2)) for h in range(24)],
        label="Hora",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    minutos = forms.ChoiceField(
        choices=[(str(m).zfill(2), str(m).zfill(2)) for m in range(0, 60, 5)],
        label="Minutos",
        widget=forms.Select(attrs={'class': 'form-select'})
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
            'nombre', 'responsable', 'proyecto', 'descripcion', 
            'lugar', 'lugar_nombre', 'lugar_direccion',
            'socias_involucradas', 'personas_involucradas', 'materiales_utilizados',
            'observaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'proyecto': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lugar': forms.Select(attrs={'class': 'form-control'}),
            'lugar_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Centro Cívico (Si no está en lista)'}),
            'lugar_direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa (Si no está en lista)'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'socias_involucradas': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'personas_involucradas': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'materiales_utilizados': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)

        if self.asociacion:
            # Filtrar responsables (socias) por asociación
            from socias.models import Socia
            self.fields['responsable'].queryset = Socia.objects.filter(asociacion=self.asociacion)
            self.fields['socias_involucradas'].queryset = Socia.objects.filter(asociacion=self.asociacion)

            # Filtrar proyectos por asociación
            from proyectos.models import Proyecto
            self.fields['proyecto'].queryset = Proyecto.objects.filter(asociacion=self.asociacion)
            
            # Filtrar entidades y lugares
            self.fields['personas_involucradas'].queryset = Persona.objects.filter(asociacion=self.asociacion)
            self.fields['materiales_utilizados'].queryset = Material.objects.filter(asociacion=self.asociacion)
            self.fields['lugar'].queryset = Lugar.objects.filter(asociacion=self.asociacion)

        # Inicializar campos personalizados si hay instancia
        if self.instance:
            if self.instance.fecha:
                self.initial['fecha_dia'] = self.instance.fecha.date()
                # Extraer hora y minutos
                self.initial['hora'] = str(self.instance.fecha.hour).zfill(2)
                # Redondear minutos al múltiplo de 5 más cercano o simplemente tomarlo
                # Para ser consistentes con el selector, tomamos el valor exacto si existe en las opciones
                # o el más cercano inferior
                minuto = self.instance.fecha.minute
                minuto_rounded = minuto - (minuto % 5)
                self.initial['minutos'] = str(minuto_rounded).zfill(2)

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
        hora = cleaned_data.get('hora')
        minutos = cleaned_data.get('minutos')

        if fecha_dia and hora and minutos:
            from datetime import time
            hora_inicio = time(int(hora), int(minutos))
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
