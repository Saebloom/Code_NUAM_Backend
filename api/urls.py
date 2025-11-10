from django.urls import path, include
from rest_framework import routers
from .views import (
    InstrumentoViewSet, MercadoViewSet, EstadoViewSet, ArchivoViewSet,
    CalificacionViewSet, CalificacionTributariaViewSet, FactorTributarioViewSet,
    UserViewSet, LogViewSet, AuditoriaViewSet,
    current_user, disable_user, login_nuam,
    admin_create_user, get_users_by_role, 
    enable_user, delete_user # <-- TODAS LAS FUNCIONES IMPORTADAS
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
    
    # 🛠️ NUEVAS RUTAS CRUD
    path('users/<int:pk>/enable/', enable_user, name='enable_user'),        # HABILITAR
    path('users/<int:pk>/delete/', delete_user, name='delete_user_perm'),  # BORRAR PERMANENTEMENTE
    path('users/admin_create/', admin_create_user, name='admin_create_user'), # CREAR
    path('users/by_role/', get_users_by_role, name='get_users_by_role'),   # ROLES
    
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