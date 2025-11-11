# nuam/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

# Importamos las vistas limpias de nuam/views.py
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
    # 1. Rutas principales
    path("", spa_entry, name="home"), # La raíz sirve el index.html
    path("logout/", custom_logout_view, name="logout"),
    path("admin/", admin.site.urls),

    # 2. Rutas de la API
    path("api/", include("api.urls")), # Aquí vive toda tu API

    # 3. Documentación
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # 4. Rutas que sirven los HTML de los dashboards
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

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)