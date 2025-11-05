from django.urls import path, include
from rest_framework import routers
from .views import (
    InstrumentoViewSet, MercadoViewSet, EstadoViewSet, ArchivoViewSet,
    CalificacionViewSet, CalificacionTributariaViewSet, FactorTributarioViewSet,
    UserViewSet
)
from .views import current_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
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

urlpatterns = [
    # user 'me' endpoint should take precedence over the router's users/ detail routes
    path('users/me/', current_user, name='current_user'),
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('health/', health_check, name='health_check'),
]
