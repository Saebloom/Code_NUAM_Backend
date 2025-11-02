from django.contrib import admin
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)

admin.site.register(Rol)
admin.site.register(Estado)
admin.site.register(Instrumento)
admin.site.register(Mercado)
admin.site.register(Archivo)
admin.site.register(Calificacion)
admin.site.register(CalificacionTributaria)
admin.site.register(FactorTributario)
admin.site.register(Log)
admin.site.register(Auditoria)
