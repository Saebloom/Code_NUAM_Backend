# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group # Importa el modelo Group
from django.contrib.auth import get_user_model # Importa la función para obtener tu Usuario
from .models import (
    Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)

# Obtiene tu modelo de Usuario personalizado (api.Usuario)
User = get_user_model()

# --- Configuración para mostrar tu Usuario personalizado ---
class CustomUserAdmin(BaseUserAdmin):
    """
    Define cómo se ve tu modelo Usuario en el panel de admin.
    """
    model = User
    # Muestra estos campos en la lista
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups_display')
    
    # Añade tus campos personalizados (RUT, país, etc.) al formulario de edición
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Datos Personales (NUAM)', {
            'fields': ('genero', 'telefono', 'direccion', 'rut_documento', 'pais')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Datos Personales (NUAM)', {
            'fields': ('first_name', 'last_name', 'email', 'genero', 'telefono', 'direccion', 'rut_documento', 'pais')
        }),
    )
    
    # Función para mostrar los grupos en la lista
    def get_groups_display(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups_display.short_description = 'Grupos'

# --- REGISTRO DE MODELOS ---

# 1. Quitamos el registro de 'Group' por defecto (si existe)
#    Esto evita errores de "ya registrado"
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# 2. Registramos 'Group' y tu 'Usuario' personalizado
admin.site.register(User, CustomUserAdmin) # <-- ESTO AÑADE "USUARIOS"
admin.site.register(Group)                  # <-- ESTO AÑADE "GRUPOS"

# 3. Registramos el resto de tus modelos de la app API
admin.site.register(Estado)
admin.site.register(Instrumento)
admin.site.register(Mercado)
admin.site.register(Archivo)
admin.site.register(Calificacion)
admin.site.register(CalificacionTributaria)
admin.site.register(FactorTributario)
admin.site.register(Log)
admin.site.register(Auditoria)