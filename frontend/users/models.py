"""
Modelos para autenticación y gestión de usuarios web
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import AsociacionVecinal
import uuid
from django.utils import timezone
from datetime import timedelta


class AdminInvitation(models.Model):
    """
    Invitaciones para nuevos administradores (superusuarios o de asociación)
    """
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    asociacion = models.ForeignKey(
        AsociacionVecinal, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name="Asociación (Dejar vacío para Superusuario)",
        help_text="Si se selecciona, el usuario será administrador de esta asociación. Si se deja vacío, será Superusuario del sistema."
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(editable=False)
    used = models.BooleanField(default=False)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="invitations_sent")

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Invitación para {self.email}"

    class Meta:
        verbose_name = "Invitación de Administrador"
        verbose_name_plural = "Invitaciones de Administradores"


class UserProfile(models.Model):
    """
    Perfil extendido de usuario vinculado a una asociación
    """
    ROLE_CHOICES = [
        ('member', 'Miembro'),
        ('admin', 'Administrador de Asociación'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Asociación Vecinal",
        help_text="Asociación a la que pertenece el usuario"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name="Rol en la Asociación"
    )

    # Información personal adicional
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    ocupacion = models.CharField(max_length=100, blank=True, verbose_name="Ocupación")

    # Metadatos
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ingreso")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        if self.asociacion:
            return f"{self.user.get_full_name() or self.user.username} - {self.asociacion.nombre}"
        return f"{self.user.get_full_name() or self.user.username} - Sin asociación"

    def is_association_admin(self):
        """Verifica si el usuario es administrador de su asociación"""
        return self.role == 'admin'

    def can_manage_users(self):
        """Verifica si el usuario puede gestionar otros usuarios"""
        return self.user.is_superuser or self.is_association_admin()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crear perfil de usuario automáticamente cuando se crea un usuario
    Nota: La asociación debe asignarse manualmente por un administrador
    """
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guardar perfil de usuario cuando se guarda el usuario
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
