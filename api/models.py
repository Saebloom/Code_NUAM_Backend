from django.db import models
from django.contrib.auth.models import User

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

class Calificacion(models.Model):
    monto_factor = models.DecimalField(max_digits=18, decimal_places=4)
    fecha_emision = models.DateField()
    fecha_pago = models.DateField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="calificaciones")
    instrumento = models.ForeignKey(Instrumento, on_delete=models.SET_NULL, null=True)
    mercado = models.ForeignKey(Mercado, on_delete=models.SET_NULL, null=True)
    archivo = models.ForeignKey(Archivo, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calificación {self.id} - {self.instrumento}"

class CalificacionTributaria(models.Model):
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, related_name="tributarias")
    secuencia_evento = models.IntegerField()
    evento_capital = models.DecimalField(max_digits=18, decimal_places=4)
    anio = models.IntegerField()
    valor_historico = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    ingreso_por_montos = models.BooleanField(default=False)

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
