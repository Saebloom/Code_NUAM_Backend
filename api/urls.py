# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UsuarioViewSet, CalificacionViewSet, LogViewSet, 
    RespaldoViewSet, InstrumentoViewSet, MercadoViewSet, EstadoViewSet
)

# Router gestiona las URLs automáticamente (RESTful)
router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='user')
router.register(r'calificaciones', CalificacionViewSet, basename='calificacion')
router.register(r'logs', LogViewSet, basename='log')
router.register(r'respaldos', RespaldoViewSet, basename='respaldo')
router.register(r'instrumentos', InstrumentoViewSet)
router.register(r'mercados', MercadoViewSet)
router.register(r'estados', EstadoViewSet)

urlpatterns = [
    # Rutas de Autenticación (JWT)
    path('auth/login_nuam/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rutas de la API generadas por el Router
    path('', include(router.urls)),
]