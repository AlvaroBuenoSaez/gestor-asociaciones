from django.db import models
from core.models import AsociacionVecinal


class Evento(models.Model):
    """Modelo para gestión de eventos y actividades"""

    EVALUACION_CHOICES = [
        (1, '⭐ Muy Malo'),
        (2, '⭐⭐ Malo'),
        (3, '⭐⭐⭐ Regular'),
        (4, '⭐⭐⭐⭐ Bueno'),
        (5, '⭐⭐⭐⭐⭐ Excelente'),
    ]

    # Relación con asociación
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    # Responsable del evento (debe ser una socia)
    responsable = models.ForeignKey(
        'socias.Socia',
        on_delete=models.PROTECT,
        related_name='eventos_responsable',
        help_text="Socia responsable del evento"
    )

    # Datos básicos
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    lugar = models.CharField(max_length=300, blank=True)

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

    # Evaluación
    evaluacion = models.PositiveSmallIntegerField(
        choices=EVALUACION_CHOICES,
        null=True,
        blank=True,
        help_text="Evaluación del evento (1-5 estrellas)"
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

    @property
    def evaluacion_display(self):
        if self.evaluacion:
            return dict(self.EVALUACION_CHOICES)[self.evaluacion]
        return "Sin evaluar"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('eventos:detail', kwargs={'pk': self.pk})
