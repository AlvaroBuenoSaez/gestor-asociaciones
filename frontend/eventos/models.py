from django.db import models
from core.models import AsociacionVecinal


class Evento(models.Model):
    """Modelo para gestión de eventos y actividades"""

    # Relación con asociación
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    # Responsable del evento (debe ser una socia)
    responsable = models.ForeignKey(
        'socias.Socia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_responsable',
        help_text="Socia responsable del evento"
    )

    # Proyecto asociado
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos',
        help_text="Proyecto al que pertenece este evento"
    )

    # Datos básicos
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    lugar_nombre = models.CharField(max_length=300, blank=True, verbose_name="Nombre del Lugar", help_text="Ej: Centro Cívico, Plaza Mayor...")
    lugar_direccion = models.CharField(max_length=500, blank=True, verbose_name="Dirección del Lugar")

    # Fechas y duración
    fecha = models.DateTimeField()
    duracion = models.DurationField(
        null=True,
        blank=True,
        help_text="Duración del evento (ej: 2:30:00 para 2h 30min)"
    )

    # Colaboradores y evaluación
    colaboradores = models.TextField(
        blank=True,
        help_text="Lista de colaboradores o entidades que participaron"
    )

    # Observaciones adicionales
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones y comentarios sobre el evento"
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('eventos:detail', kwargs={'pk': self.pk})


class Lugar(models.Model):
    nombre = models.CharField(max_length=300, unique=True)
    direccion = models.CharField(max_length=500)

    class Meta:
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"
        db_table = "lugares"

    def __str__(self):
        return self.nombre
