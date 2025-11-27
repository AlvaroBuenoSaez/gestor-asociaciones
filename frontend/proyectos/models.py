from django.db import models
from core.models import AsociacionVecinal


class Proyecto(models.Model):
    """Modelo para gestión de proyectos de la asociación"""

    # Relación con asociación
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='proyectos'
    )

    # Datos básicos
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del proyecto"
    )
    responsable = models.ForeignKey(
        'socias.Socia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos_responsable',
        help_text="Socia responsable del proyecto"
    )
    involucrados = models.TextField(
        blank=True,
        help_text="Lista de personas involucradas en el proyecto (Texto libre)"
    )
    
    # Relaciones con personas y socias
    socias_involucradas = models.ManyToManyField(
        'socias.Socia',
        blank=True,
        related_name='proyectos_involucrada',
        help_text="Socias que participan en el proyecto"
    )
    personas_involucradas = models.ManyToManyField(
        'entidades.Persona',
        blank=True,
        related_name='proyectos_involucrada',
        help_text="Personas externas que participan en el proyecto"
    )

    descripcion = models.TextField(
        blank=True,
        help_text="Descripción detallada del proyecto"
    )

    # Recursos y ubicación
    materiales = models.TextField(
        blank=True,
        help_text="Lista de materiales necesarios (Texto libre)"
    )
    materiales_necesarios = models.ManyToManyField(
        'entidades.Material',
        blank=True,
        related_name='proyectos',
        help_text="Materiales del inventario necesarios"
    )

    lugar = models.CharField(
        max_length=300,
        blank=True,
        help_text="Ubicación donde se desarrolla el proyecto (Texto libre)"
    )
    lugar_fk = models.ForeignKey(
        'eventos.Lugar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos',
        verbose_name="Lugar (Selección)",
        help_text="Lugar registrado en el sistema"
    )

    # Fechas del proyecto
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio del proyecto"
    )
    fecha_final = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de finalización prevista"
    )

    # Configuración
    recursivo = models.BooleanField(
        default=False,
        help_text="¿Es un proyecto que se repite periódicamente?"
    )

    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} - {self.responsable}"

    @property
    def estado(self):
        """Determina el estado del proyecto basado en las fechas"""
        from django.utils import timezone
        hoy = timezone.now().date()

        if hoy < self.fecha_inicio:
            return "pendiente"
        elif self.fecha_final and hoy > self.fecha_final:
            return "finalizado"
        else:
            return "en_curso"

    @property
    def estado_display(self):
        """Retorna el estado del proyecto en formato legible"""
        estados = {
            'pendiente': '⏳ Pendiente',
            'en_curso': '🔄 En Curso',
            'finalizado': '✅ Finalizado'
        }
        return estados.get(self.estado, '❓ Desconocido')

    @property
    def duracion_dias(self):
        """Calcula la duración en días del proyecto"""
        if self.fecha_final:
            return (self.fecha_final - self.fecha_inicio).days
        return None

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('proyectos:detail', kwargs={'pk': self.pk})
