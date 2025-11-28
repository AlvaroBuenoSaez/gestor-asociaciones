from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.db import models
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from core.models import AsociacionVecinal
from .models import UserProfile, AdminInvitation


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

@admin.register(AdminInvitation)
class AdminInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'asociacion', 'created_at', 'expires_at', 'used', 'invited_by', 'status_display')
    readonly_fields = ('token', 'created_at', 'expires_at', 'used', 'invited_by')
    
    def save_model(self, request, obj, form, change):
        if not change: # Creating new
            obj.invited_by = request.user
            super().save_model(request, obj, form, change)
            
            # Send email
            try:
                path = reverse('users:accept_invite', args=[obj.token])
                full_url = request.build_absolute_uri(path)
                
                tipo_usuario = f"administrador de {obj.asociacion}" if obj.asociacion else "Superusuario"
                
                send_mail(
                    'Invitación para Administrador - Gestor Asociaciones',
                    f'Hola,\n\nHas sido invitado para ser {tipo_usuario}.\n\nHaz clic aquí para registrarte (válido por 15 min): {full_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.email],
                    fail_silently=False,
                )
                self.message_user(request, f"Invitación enviada a {obj.email}")
            except Exception as e:
                self.message_user(request, f"Error enviando email: {str(e)}", level='ERROR')
        else:
            super().save_model(request, obj, form, change)

    def status_display(self, obj):
        if obj.used:
            return "Usada"
        if obj.is_valid:
            return "Válida"
        return "Expirada"
    status_display.short_description = "Estado"


# Configuración del sitio admin
admin.site.site_header = "AsoNet - Administración"
admin.site.site_title = "AsoNet Admin"
admin.site.index_title = "Gestión de Asociaciones Vecinales"