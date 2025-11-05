from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class TimeStampedModel(models.Model):
    """Modelo base abstracto que proporciona campos de auditoría"""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created",
        verbose_name="Creado por"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_updated",
        verbose_name="Actualizado por"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Asegura que updated_at se actualice en cada save y created_at se establezca solo al crear."""
        if not self.pk and not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class AuditableModel(TimeStampedModel):
    """Modelo base abstracto que agrega campos de auditoría adicionales"""
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")

    class Meta:
        abstract = True

    def soft_delete(self, user):
        """Realiza un borrado suave del registro"""
        self.is_active = False
        self.updated_by = user
        self.save()

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Estado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Instrumento(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    moneda = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Mercado(models.Model):
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Archivo(models.Model):
    nombre_archivo = models.CharField(max_length=255)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    estado_validacion = models.CharField(max_length=100, default="pendiente")
    ruta = models.CharField(max_length=500, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_archivo

class Calificacion(AuditableModel):
    monto_factor = models.DecimalField(
        max_digits=18, 
        decimal_places=4, 
        db_index=True,
        verbose_name="Monto Factor"
    )
    fecha_emision = models.DateField(
        db_index=True,
        verbose_name="Fecha de Emisión"
    )
    fecha_pago = models.DateField(
        db_index=True,
        verbose_name="Fecha de Pago"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="calificaciones",
        verbose_name="Usuario"
    )
    instrumento = models.ForeignKey(
        Instrumento, 
        on_delete=models.SET_NULL, 
        null=True, 
        db_index=True,
        verbose_name="Instrumento"
    )
    mercado = models.ForeignKey(
        Mercado, 
        on_delete=models.SET_NULL, 
        null=True, 
        db_index=True,
        verbose_name="Mercado"
    )
    archivo = models.ForeignKey(
        Archivo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Archivo"
    )
    estado = models.ForeignKey(
        Estado, 
        on_delete=models.SET_NULL, 
        null=True, 
        db_index=True,
        verbose_name="Estado"
    )

    class Meta:
        indexes = [
            models.Index(fields=['fecha_emision', 'estado']),
            models.Index(fields=['usuario', 'created_at']),
            models.Index(fields=['instrumento', 'mercado']),
        ]
        ordering = ['-created_at']
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"

    def clean(self):
        if self.fecha_pago < self.fecha_emision:
            raise ValidationError({
                'fecha_pago': 'La fecha de pago no puede ser anterior a la fecha de emisión'
            })
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Calificación {self.id} - {self.instrumento}"

class CalificacionTributaria(AuditableModel):
    calificacion = models.ForeignKey(
        Calificacion, 
        on_delete=models.CASCADE, 
        related_name="tributarias",
        verbose_name="Calificación"
    )
    secuencia_evento = models.IntegerField(
        verbose_name="Secuencia del Evento",
        help_text="Número que indica el orden del evento"
    )
    evento_capital = models.DecimalField(
        max_digits=18, 
        decimal_places=4,
        verbose_name="Evento Capital"
    )
    anio = models.IntegerField(
        verbose_name="Año",
        db_index=True
    )
    valor_historico = models.DecimalField(
        max_digits=18, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name="Valor Histórico"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    ingreso_por_montos = models.BooleanField(
        default=False,
        verbose_name="Ingreso por Montos"
    )

    class Meta:
        ordering = ['calificacion', 'secuencia_evento']
        verbose_name = "Calificación Tributaria"
        verbose_name_plural = "Calificaciones Tributarias"
        indexes = [
            models.Index(fields=['anio', 'calificacion']),
            models.Index(fields=['secuencia_evento'])
        ]

    def clean(self):
        if self.valor_historico and self.valor_historico > self.evento_capital:
            raise ValidationError({
                'valor_historico': 'El valor histórico no puede ser mayor al evento capital'
            })

    def __str__(self):
        return f"Tributaria {self.id} para Calificacion {self.calificacion_id}"

class FactorTributario(models.Model):
    calificacion_tributaria = models.ForeignKey(CalificacionTributaria, on_delete=models.CASCADE, related_name="factores")
    codigo_factor = models.CharField(max_length=100)
    descripcion_factor = models.CharField(max_length=255)
    valor_factor = models.DecimalField(max_digits=18, decimal_places=8)

    def __str__(self):
        return f"{self.codigo_factor} ({self.valor_factor})"

class Log(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=200)
    detalle = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    calificacion = models.ForeignKey(Calificacion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.fecha} - {self.accion}"

class Auditoria(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=100)
    resultado = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    calificacion = models.ForeignKey(Calificacion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Auditoria {self.id} - {self.tipo}"
