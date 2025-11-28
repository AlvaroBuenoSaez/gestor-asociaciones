"""
Formularios para el módulo users
Consolidación de todos los formularios en un solo archivo organizado
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import AsociacionVecinal
from .models import UserProfile


# =============================================================================
# FORMULARIOS PARA GESTIÓN DE USUARIOS WEB (Simples para administradores)
# =============================================================================

class SimpleUserForm(UserCreationForm):
    """Formulario simplificado para crear usuarios web"""

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='member',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class EditUserForm(forms.ModelForm):
    """Formulario para editar usuarios existentes"""

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar el campo role con el valor actual del usuario
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['role'].initial = self.instance.profile.role


class AdminRegistrationForm(UserCreationForm):
    """Formulario para registro de administradores invitados"""
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


# =============================================================================
# FORMULARIOS PARA GESTIÓN DE ASOCIACIONES (Para superusuarios)
# =============================================================================

class AsociacionForm(forms.ModelForm):
    """Formulario para crear/editar asociaciones"""

    class Meta:
        model = AsociacionVecinal
        fields = ['nombre', 'direccion', 'telefono', 'email', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la asociación'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123-456-789'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@asociacion.com'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción de la asociación...'}),
        }


class UserProfileForm(forms.ModelForm):
    """Formulario para gestionar perfiles de usuario"""

    class Meta:
        model = UserProfile
        fields = ['role', 'asociacion']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'asociacion': forms.Select(attrs={'class': 'form-select'}),
        }


# =============================================================================
# FORMULARIOS AVANZADOS PARA SUPERUSUARIOS
# =============================================================================

class CustomUserCreationForm(UserCreationForm):
    """Formulario extendido para crear usuarios con perfil"""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='member',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    asociacion = forms.ModelChoiceField(
        queryset=AsociacionVecinal.objects.all(),
        empty_label="Selecciona una asociación",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.asociacion = self.cleaned_data['asociacion']
            profile.save()

        return user


# =============================================================================
# FORMULARIOS ACTIVOS
# Formularios específicos implementados en sus respectivas apps:
# - SociaForm: socias/forms.py
# - EventoForm: eventos/forms.py (cuando se implemente)
# - TransaccionForm: finanzas/forms.py (cuando se implemente)
# - ProyectoForm: proyectos/forms.py (cuando se implemente)
# =============================================================================