from django.urls import path, include
from rest_framework import routers
from .views import (
    InstrumentoViewSet, MercadoViewSet, EstadoViewSet, ArchivoViewSet,
    CalificacionViewSet, CalificacionTributariaViewSet, FactorTributarioViewSet,
    UserViewSet, LogViewSet, AuditoriaViewSet,
    current_user, disable_user, login_nuam
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .monitoring import health_check

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'instrumentos', InstrumentoViewSet)
router.register(r'mercados', MercadoViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'archivos', ArchivoViewSet)
router.register(r'calificaciones', CalificacionViewSet)
router.register(r'calificacion-tributaria', CalificacionTributariaViewSet)
router.register(r'factor-tributario', FactorTributarioViewSet)
router.register(r'logs', LogViewSet, basename='logs')
router.register(r'auditorias', AuditoriaViewSet, basename='auditorias')

urlpatterns = [
    # Usuarios
    path('users/me/', current_user, name='current_user'),
    path('users/<int:pk>/disable/', disable_user, name='disable_user'),

    # Router de los viewsets
    path('', include(router.urls)),

    # JWT Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Login corporativo NUAM
    path("auth/login_nuam/", login_nuam, name="login_nuam"),

    # Health check
    path("health/", health_check, name="health_check"),
]
