from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

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
    # 🏠 Página de inicio (login, registro y recuperar)
    path("", TemplateView.as_view(template_name="index.html"), name="home"),

    # 📊 Dashboards según el rol (se sirven directo desde /templates/)
    path("dashboard/admin/", TemplateView.as_view(template_name="admin/dashboard.html"), name="dashboard_admin"),
    path("dashboard/corredor/", TemplateView.as_view(template_name="corredor/dashboard_corredor.html"), name="dashboard_corredor"),
    path("dashboard/supervisor/", TemplateView.as_view(template_name="supervisor/dashboard_supervisor.html"), name="dashboard_supervisor"),

    # ⚙️ Django Admin y API REST
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),

    # 📚 Swagger / Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
