from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import (
    login_view,
    dashboard_admin,
    dashboard_corredor,
    dashboard_supervisor,
    logout_view
)

schema_view = get_schema_view(
    openapi.Info(
        title="NUAM API",
        default_version='v1',
        description="API para el sistema NUAM",
        contact=openapi.Contact(email="contact@nuam.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Home/Login
    path("", login_view, name="home"),
    
    # Dashboards (Vistas de sesión de Django)
    path("dashboard/admin/", dashboard_admin, name="dashboard_admin"),
    path("dashboard/corredor/", dashboard_corredor, name="dashboard_corredor"),
    path("dashboard/supervisor/", dashboard_supervisor, name="dashboard_supervisor"),

    # Admin y API
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Logout
    path("logout/", logout_view, name="logout"),

    # -----------------------------------------------------------------
    # 🛠️ CORRECCIÓN: Rutas de TemplateView para la API (JWT/SPA)
    # -----------------------------------------------------------------
    # (Apunta a las subcarpetas correctas)
    
    path('template/home/', TemplateView.as_view(template_name="index.html"), name='template_home'),
    
    path('template/dashboard/admin/', 
         TemplateView.as_view(template_name="Admin (superusuario)/dashboard.html"), 
         name='template_dashboard_admin'),
         
    path('template/dashboard/corredor/', 
         TemplateView.as_view(template_name="Corredor/dashboard_corredor.html"), 
         name='template_dashboard_corredor'),
         
    path('template/dashboard/supervisor/', 
         TemplateView.as_view(template_name="Supervisor/dashboard_supervisor.html"), 
         name='template_dashboard_supervisor'),
         
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)