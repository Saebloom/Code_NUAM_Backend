from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth, TruncYear
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)

admin.site.site_header = "NUAM Administration"
admin.site.site_title = "NUAM Admin Portal"
admin.site.index_title = "Bienvenido al Portal Administrativo de NUAM"

class DashboardAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Estadísticas generales
        total_calificaciones = Calificacion.objects.count()
        total_usuarios = User.objects.count()
        total_instrumentos = Instrumento.objects.count()

        # Calificaciones por mes
        calificaciones_mes = (
            Calificacion.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )

        # Calificaciones por estado
        calificaciones_estado = (
            Calificacion.objects
            .values('estado__nombre')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        context = {
            'total_calificaciones': total_calificaciones,
            'total_usuarios': total_usuarios,
            'total_instrumentos': total_instrumentos,
            'calificaciones_mes': list(calificaciones_mes),
            'calificaciones_estado': list(calificaciones_estado),
        }

        return render(request, 'admin/dashboard.html', context)

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'monto_factor', 'fecha_emision', 'fecha_pago', 'usuario', 'instrumento', 'estado', 'created_at')
    list_filter = ('estado', 'mercado', 'fecha_emision', 'is_active')
    search_fields = ('instrumento__nombre', 'usuario__username', 'mercado__nombre')
    date_hierarchy = 'fecha_emision'
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    list_per_page = 20
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una creación nueva
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

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
    list_display = ('id', 'calificacion', 'secuencia_evento', 'evento_capital', 'anio', 'is_active')
    list_filter = ('anio', 'ingreso_por_montos', 'is_active')
    search_fields = ('calificacion__instrumento__nombre',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

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
