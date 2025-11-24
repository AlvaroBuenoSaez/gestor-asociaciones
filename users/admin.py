from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.db import models
from core.models import AsociacionVecinal
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline para editar perfil de usuario dentro del admin de User
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Información de Asociación'
    fields = ('asociacion', 'role', 'telefono', 'direccion', 'fecha_nacimiento', 'ocupacion')

    # Hacer la asociación obligatoria
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['asociacion'].required = True
        return formset


class CustomUserAdmin(UserAdmin):
    """
    Admin personalizado para usuarios - integra perfil de asociación
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_asociacion', 'get_role', 'is_active')
    list_filter = ('is_active', 'profile__asociacion', 'profile__role')

    # Personalizar fieldsets para incluir campos obligatorios
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )

    def get_asociacion(self, obj):
        if hasattr(obj, 'profile') and obj.profile.asociacion:
            return obj.profile.asociacion.nombre
        return "⚠️ Sin asociación"
    get_asociacion.short_description = 'Asociación'

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return "Sin perfil"
    get_role.short_description = 'Rol'


# Desregistrar elementos que no necesitamos
admin.site.unregister(User)
admin.site.unregister(Group)  # Ocultar grupos - no los necesitamos

# Registrar nuestro admin personalizado
admin.site.register(User, CustomUserAdmin)

# Configuración del sitio admin
admin.site.site_header = "AsoNet - Administración"
admin.site.site_title = "AsoNet Admin"
admin.site.index_title = "Gestión de Asociaciones Vecinales"