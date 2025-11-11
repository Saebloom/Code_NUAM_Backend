from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings 
# Importar User (aunque se usa settings.AUTH_USER_MODEL, lo mantenemos por claridad)
from django.contrib.auth.models import User 


# -----------------------------
# 👤 MODELO DE USUARIO PERSONALIZADO (Hereda de AbstractUser)
# -----------------------------
class Usuario(AbstractUser):
    GENERO_CHOICES = [
        ("Masculino", "Masculino"),
        ("Femenino", "Femenino"),
        ("Otro", "Otro"),
    ]

    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    
    # 🛠️ CAMPOS DE DOCUMENTO (AÑADIDOS)
    rut_documento = models.CharField(max_length=12, blank=True, null=True, unique=True, verbose_name="RUT / Documento")
    pais = models.CharField(max_length=50, blank=True, null=True, verbose_name="País")


    def __str__(self):
        # Muestra nombre y apellido si existen, si no, solo el username
        return f"{self.first_name} {self.last_name} ({self.username})" if self.first_name else self.username

# -----------------------------
# 🕓 MODELOS BASE DE AUDITORÍA
# -----------------------------
class TimeStampedModel(models.Model):
    """Modelo base abstracto que proporciona campos de auditoría"""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_updated"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class AuditableModel(TimeStampedModel):
    """Modelo base abstracto que agrega campos de auditoría adicionales"""
    is_active = models.BooleanField(default=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def soft_delete(self, user):
        """Realiza un borrado suave del registro"""
        self.is_active = False
        self.updated_by = user
        self.save()


# -----------------------------
# 📋 MODELOS DEL SISTEMA
# -----------------------------


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
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.nombre_archivo

# ----- Calificaciones -----
class Calificacion(AuditableModel):
    monto_factor = models.DecimalField(max_digits=18, decimal_places=4, db_index=True)
    fecha_emision = models.DateField(db_index=True)
    fecha_pago = models.DateField(db_index=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="calificaciones")
    instrumento = models.ForeignKey('Instrumento', on_delete=models.SET_NULL, null=True, db_index=True)
    mercado = models.ForeignKey('Mercado', on_delete=models.SET_NULL, null=True, db_index=True)
    archivo = models.ForeignKey('Archivo', on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey('Estado', on_delete=models.SET_NULL, null=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_emision', 'estado']),
            models.Index(fields=['usuario', 'created_at']),
            models.Index(fields=['instrumento', 'mercado']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.fecha_pago < self.fecha_emision:
            raise ValidationError({'fecha_pago': 'La fecha de pago no puede ser anterior a la fecha de emisión'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Calificación {self.id} - {self.instrumento}"

class CalificacionTributaria(AuditableModel):
    calificacion = models.ForeignKey('Calificacion', on_delete=models.CASCADE, related_name="tributarias")
    secuencia_evento = models.IntegerField()
    evento_capital = models.DecimalField(max_digits=18, decimal_places=4)
    anio = models.IntegerField(db_index=True)
    valor_historico = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    ingreso_por_montos = models.BooleanField(default=False)

    class Meta:
        ordering = ['calificacion', 'secuencia_evento']

    def clean(self):
        if self.valor_historico and self.valor_historico > self.evento_capital:
            raise ValidationError({'valor_historico': 'El valor histórico no puede ser mayor al evento capital'})

    def __str__(self):
        return f"Tributaria {self.id} para Calificación {self.calificacion_id}"

class FactorTributario(models.Model):
    calificacion_tributaria = models.ForeignKey('CalificacionTributaria', on_delete=models.CASCADE, related_name="factores")
    codigo_factor = models.CharField(max_length=100)
    descripcion_factor = models.CharField(max_length=255)
    valor_factor = models.DecimalField(max_digits=18, decimal_places=8)
    def __str__(self):
        return f"{self.codigo_factor} ({self.valor_factor})"

class Log(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=200)
    detalle = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    calificacion = models.ForeignKey('Calificacion', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.fecha} - {self.accion}"

class Auditoria(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=100)
    resultado = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    calificacion = models.ForeignKey('Calificacion', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"Auditoría {self.id} - {self.tipo}"