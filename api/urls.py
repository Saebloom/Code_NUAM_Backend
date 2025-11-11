# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views # Importa api/views.py

# Configuración del Router para los ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'calificaciones', views.CalificacionViewSet, basename='calificacion')
router.register(r'instrumentos', views.InstrumentoViewSet, basename='instrumento')
router.register(r'mercados', views.MercadoViewSet, basename='mercado')
router.register(r'estados', views.EstadoViewSet, basename='estado')
router.register(r'archivos', views.ArchivoViewSet, basename='archivo')
router.register(r'calificaciones-tributarias', views.CalificacionTributariaViewSet, basename='calificaciontributaria')
router.register(r'factores-tributarios', views.FactorTributarioViewSet, basename='factortributario')

# Arreglo: Añadir los ViewSets de Log y Auditoria que faltaban
router.register(r'logs', views.LogViewSet, basename='log')
router.register(r'auditorias', views.AuditoriaViewSet, basename='auditoria')

# Arreglo: Eliminar el 'RolViewSet' que ya no existe
# router.register(r'roles', views.RolViewSet, basename='rol') # <-- Esta línea se elimina si ya limpiaste el modelo Rol

urlpatterns = [
    # --- Rutas de API generadas por el Router ---
    path('', include(router.urls)),
    
    # --- Ruta de Health Check (si la tienes, del archivo monitoring.py) ---
    # path('health/', views.health_check, name='health-check'), 
    
    # --- Rutas de Autenticación (Personalizada) ---
    path('auth/login_nuam/', views.login_nuam, name='login_nuam'),
]

# NOTA: Tus rutas personalizadas para @action (como 'me', 'disable_user')
# ya están incluidas automáticamente por el 'router' de arriba.
# No necesitas las líneas 'path('users/me/', ...)' que tenías antes.