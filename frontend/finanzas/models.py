from django.db import models
from core.models import AsociacionVecinal


class Transaccion(models.Model):
    """Modelo para gestión de transacciones financieras"""

    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    # Relación con asociación
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='transacciones'
    )

    # Datos financieros
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Positivo para ingresos, negativo para gastos"
    )
    concepto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    # Fechas
    fecha_transaccion = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    # Relaciones opcionales
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones'
    )
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones'
    )
    socia = models.ForeignKey(
        'socias.Socia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones'
    )
    entidad = models.CharField(
        max_length=200,
        blank=True,
        help_text="Banco, proveedor, etc."
    )

    # Google Drive Integration
    drive_file_id = models.CharField(max_length=100, blank=True, null=True)
    drive_file_link = models.URLField(blank=True, null=True)
    drive_file_name = models.CharField(max_length=255, blank=True, null=True)

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-fecha_transaccion']

    def __str__(self):
        tipo = "Ingreso" if self.cantidad >= 0 else "Gasto"
        return f"{tipo}: {self.concepto} - {self.cantidad}€"

    @property
    def tipo(self):
        return 'ingreso' if self.cantidad >= 0 else 'gasto'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:detail', kwargs={'pk': self.pk})
