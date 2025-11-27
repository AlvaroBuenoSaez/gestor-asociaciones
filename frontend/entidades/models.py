from django.db import models
from core.models import AsociacionVecinal
from decimal import Decimal

class Entidad(models.Model):
    """Modelo para entidades externas (empresas, instituciones, otras asociaciones)"""
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='entidades_externas'
    )
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100, blank=True, help_text="Ej: Ayuntamiento, Empresa, Asociación...")
    descripcion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    web = models.URLField(blank=True)
    direccion = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Persona(models.Model):
    """Modelo para personas externas/contactos"""
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='personas_externas'
    )
    entidad = models.ForeignKey(
        Entidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personas',
        help_text="Entidad a la que pertenece (opcional)"
    )
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200, blank=True)
    contacto = models.CharField(max_length=200, blank=True, help_text="Información de contacto adicional o rol")
    cargo = models.CharField(max_length=100, blank=True, help_text="Cargo en la entidad o relación")
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    observaciones = models.TextField(blank=True)

    # Relaciones
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personas_externas',
        help_text="Proyecto en el que participa"
    )
    le_conoce = models.ManyToManyField(
        'socias.Socia',
        blank=True,
        related_name='conocidos_externos',
        help_text="Socias que conocen a esta persona"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['nombre', 'apellidos']

    def __str__(self):
        return f"{self.nombre} {self.apellidos}".strip()


class Material(models.Model):
    """Modelo para gestión de materiales e inventario"""
    asociacion = models.ForeignKey(
        AsociacionVecinal,
        on_delete=models.CASCADE,
        related_name='materiales'
    )
    nombre = models.CharField(max_length=200)
    uso = models.TextField(blank=True, help_text="Para qué se utiliza este material")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Valor estimado o precio de compra")

    # Relaciones
    transaccion_compra = models.ForeignKey(
        'finanzas.Transaccion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales_comprados',
        help_text="Transacción de compra asociada (opcional)"
    )
    lugar = models.ForeignKey(
        'eventos.Lugar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales',
        help_text="Ubicación del material"
    )

    # Encargado (Polimórfico simple)
    encargado_persona = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales_a_cargo',
        help_text="Persona externa encargada"
    )
    encargado_socia = models.ForeignKey(
        'socias.Socia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales_a_cargo',
        help_text="Socia encargada"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def encargado(self):
        if self.encargado_socia:
            return f"{self.encargado_socia} (Socia)"
        elif self.encargado_persona:
            return f"{self.encargado_persona} (Externo)"
        return "Sin asignar"
