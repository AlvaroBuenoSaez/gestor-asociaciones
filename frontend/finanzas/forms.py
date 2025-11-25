from django import forms
from .models import Transaccion

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = [
            'cantidad', 'concepto', 'descripcion',
            'fecha_transaccion', 'fecha_vencimiento',
            'evento', 'proyecto', 'socia', 'entidad'
        ]
        widgets = {
            'fecha_transaccion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
            'entidad': forms.TextInput(attrs={'class': 'form-control'}),
            'evento': forms.Select(attrs={'class': 'form-select'}),
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'socia': forms.Select(attrs={'class': 'form-select'}),
        }
