# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
from api.monitoring import health_check # Asumiendo que aún tienes monitoring.py

# Configuración del Router para los ViewSets
router = DefaultRouter()

# REGISTRO AUTOMÁTICO DE RUTAS (Esto arregla el 404)
# Esto crea /users/, /users/{pk}/, y TODAS las @action (como disable_user, admin_create, etc.)
router.register(r'users', views.UserViewSet, basename='user')

# Resto de tus ViewSets
router.register(r'calificaciones', views.CalificacionViewSet, basename='calificacion')
router.register(r'instrumentos', views.InstrumentoViewSet, basename='instrumento')
router.register(r'mercados', views.MercadoViewSet, basename='mercado')
router.register(r'estados', views.EstadoViewSet, basename='estado')
router.register(r'archivos', views.ArchivoViewSet, basename='archivo')
router.register(r'calificaciones-tributarias', views.CalificacionTributariaViewSet, basename='calificaciontributaria')
router.register(r'factores-tributarios', views.FactorTributarioViewSet, basename='factortributario')
router.register(r'logs', views.LogViewSet, basename='log')
router.register(r'auditorias', views.AuditoriaViewSet, basename='auditoria')


urlpatterns = [
    # --- Rutas de API generadas por el Router ---
    path('', include(router.urls)),
    
    # --- Ruta de Health Check ---
    path('health/', health_check, name='health-check'),
    
    # --- Ruta de Autenticación (Personalizada) ---
    path('auth/login_nuam/', views.login_nuam, name='login_nuam'),
]