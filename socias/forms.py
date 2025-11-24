"""
Formularios personalizados para la app socias
"""
from django import forms
from django.db.models import Max
from .models import Socia


class SociaForm(forms.ModelForm):
    """Formulario personalizado para crear/editar socias con auto-asignación de número"""

    class Meta:
        model = Socia
        fields = [
            'numero_socia', 'nombre', 'apellidos', 'telefono',
            'direccion', 'provincia', 'codigo_postal', 'pais',
            'nacimiento', 'pagado', 'descripcion'
        ]
        widgets = {
            'numero_socia': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'placeholder': 'Se asignará automáticamente'
            }),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)

        # Si es creación (no hay instance), auto-asignar el número
        if not self.instance.pk and self.asociacion:
            self.fields['numero_socia'].initial = self._get_next_numero()
            self.fields['numero_socia'].widget.attrs.update({
                'readonly': True,
                'placeholder': 'Se asignará automáticamente'
            })
        elif self.instance.pk:
            # En edición, hacer el número readonly
            self.fields['numero_socia'].widget.attrs.update({
                'readonly': True,
                'style': 'background-color: #f8f9fa;'
            })

    def _get_next_numero(self):
        """Calcula el siguiente número de socia disponible para la asociación"""
        if not self.asociacion:
            return "1"

        # Buscar el número más alto en la asociación
        max_numero = Socia.objects.filter(
            asociacion=self.asociacion
        ).aggregate(
            max_num=Max('numero_socia')
        )['max_num']

        if max_numero:
            try:
                # Intentar convertir a entero y sumar 1
                return str(int(max_numero) + 1)
            except ValueError:
                # Si no es un número, buscar el siguiente entero disponible
                return self._find_next_available_number()
        else:
            # Primera socia de la asociación
            return "1"

    def _find_next_available_number(self):
        """Encuentra el siguiente número entero disponible"""
        if not self.asociacion:
            return "1"

        existing_numbers = set()
        socias = Socia.objects.filter(asociacion=self.asociacion)

        for socia in socias:
            try:
                existing_numbers.add(int(socia.numero_socia))
            except ValueError:
                continue  # Ignorar números no enteros

        # Encontrar el primer número disponible empezando desde 1
        numero = 1
        while numero in existing_numbers:
            numero += 1

        return str(numero)

    def save(self, commit=True):
        """Guardar la socia asignando automáticamente la asociación y el número"""
        instance = super().save(commit=False)

        if self.asociacion and not instance.asociacion_id:
            instance.asociacion = self.asociacion

        # Si es creación y no tiene número, asignarlo
        if not instance.pk and not instance.numero_socia:
            instance.numero_socia = self._get_next_numero()

        if commit:
            instance.save()

        return instance