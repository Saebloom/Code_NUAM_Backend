# nuam/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

# 1. Importamos las vistas LIMPIAS de nuam/views.py
from .views import (
    spa_entry, 
    custom_logout_view,
    AdminDashboardView,
    CorredorDashboardView,
    SupervisorDashboardView
)

schema_view = get_schema_view(
   openapi.Info(
      title="NUAM API",
      default_version='v1',
      description="API para el sistema NUAM",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # 1. La raíz sirve el index.html (punto de entrada del SPA)
    path("", spa_entry, name="home"), 

    # 2. Ruta para el logout (limpia la sesión del admin)
    path("logout/", custom_logout_view, name="logout"),
    
    # 3. Rutas de Admin y API (¡Importantes!)
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")), # Aquí vive toda tu API

    # 4. Documentación
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # 5. Rutas que sirven los HTML de los dashboards.
    # El JS de tu index.html redirige a estas.
    path('template/dashboard/admin/', 
         AdminDashboardView.as_view(), 
         name='template_dashboard_admin'),
         
    path('template/dashboard/corredor/', 
         CorredorDashboardView.as_view(), 
         name='template_dashboard_corredor'),
         
    path('template/dashboard/supervisor/', 
         SupervisorDashboardView.as_view(), 
         name='template_dashboard_supervisor'),
]

# Servir archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)