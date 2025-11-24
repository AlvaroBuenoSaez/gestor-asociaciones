"""
Modelos centrales del sistema - App Core
Contiene los modelos base que son utilizados por otras apps
"""
from django.db import models


class AsociacionVecinal(models.Model):
    """
    Modelo base para las asociaciones vecinales
    Este modelo es usado por todas las demás apps del sistema
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Asociación")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email de contacto")
    numero_registro = models.CharField(max_length=50, unique=True, verbose_name="Número de Registro")
    drive_folder_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Carpeta Google Drive")
    drive_credentials = models.TextField(blank=True, null=True, verbose_name="Credenciales Drive (JSON)")
    distrito = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    codigo_postal = models.CharField(max_length=10, blank=True, verbose_name="Código Postal")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Asociación Vecinal"
        verbose_name_plural = "Asociaciones Vecinales"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.numero_registro})"

    def get_total_members(self):
        """Devuelve el número total de miembros de la asociación"""
        return self.userprofile_set.count()
