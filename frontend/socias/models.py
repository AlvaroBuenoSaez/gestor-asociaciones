from django.db import models
from core.models import AsociacionVecinal


class Socia(models.Model):
    """Modelo para gestión de socias de la asociación"""

    # Relación con asociación
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='socias'
    )

    # Datos personales
    numero_socia = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    pais = models.CharField(max_length=100, default='España')

    # Fechas
    nacimiento = models.DateField(null=True, blank=True)
    fecha_inscripcion = models.DateField(auto_now_add=True)

    # Estado y detalles
    pagado = models.BooleanField(default=False, help_text="¿Ha pagado la cuota?")
    descripcion = models.TextField(blank=True, help_text="Notas adicionales")

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Socia"
        verbose_name_plural = "Socias"
        ordering = ['numero_socia']
        unique_together = ['asociacion', 'numero_socia']

    def __str__(self):
        return f"{self.numero_socia} - {self.nombre} {self.apellidos}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('socias:detail', kwargs={'pk': self.pk})
