from django.contrib import admin
from django.db.models import Count, Sum
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'monto_factor', 'fecha_emision', 'fecha_pago', 'usuario', 'instrumento', 'estado')
    list_filter = ('estado', 'mercado', 'fecha_emision')
    search_fields = ('instrumento__nombre', 'usuario__username', 'mercado__nombre')
    date_hierarchy = 'fecha_emision'
    readonly_fields = ('fecha_registro',)
    list_per_page = 20

@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'moneda')
    list_filter = ('tipo', 'moneda')
    search_fields = ('nombre', 'tipo')

@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'tipo')
    list_filter = ('pais', 'tipo')
    search_fields = ('nombre', 'pais')

@admin.register(CalificacionTributaria)
class CalificacionTributariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'calificacion', 'secuencia_evento', 'evento_capital', 'anio')
    list_filter = ('anio', 'ingreso_por_montos')
    search_fields = ('calificacion__instrumento__nombre',)

@admin.register(FactorTributario)
class FactorTributarioAdmin(admin.ModelAdmin):
    list_display = ('codigo_factor', 'descripcion_factor', 'valor_factor', 'calificacion_tributaria')
    search_fields = ('codigo_factor', 'descripcion_factor')
    list_filter = ('codigo_factor',)

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'accion', 'usuario', 'calificacion')
    list_filter = ('accion', 'fecha', 'usuario')
    search_fields = ('accion', 'detalle', 'usuario__username')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)

@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = ('nombre_archivo', 'fecha_carga', 'estado_validacion', 'usuario')
    list_filter = ('estado_validacion', 'fecha_carga')
    search_fields = ('nombre_archivo', 'usuario__username')
    date_hierarchy = 'fecha_carga'

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'resultado', 'usuario', 'calificacion')
    list_filter = ('tipo', 'resultado', 'fecha')
    search_fields = ('tipo', 'resultado', 'observaciones')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)
