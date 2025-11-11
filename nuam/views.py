# nuam/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import logout

def spa_entry(request):
    """
    Esta vista sirve el index.html, que es el punto de entrada
    de tu Aplicación de Página Única (SPA).
    """
    # Sirve el index.html que contiene tu login de API
    return render(request, "index.html")

def custom_logout_view(request):
    """
    Maneja el logout. El JS de tus dashboards llama a esta URL
    para limpiar la sesión de Django (ej. si estabas en /admin)
    antes de redirigir al login en el frontend.
    """
    logout(request)
    # Redirige al 'home', que es el spa_entry (index.html)
    return redirect('home')

# Vistas de Template para los Dashboards
# Simplemente sirven los archivos HTML. El JS de cada
# dashboard se encarga de la lógica.

class AdminDashboardView(TemplateView):
    # Esta ruta la usa tu JS para cargar el dashboard de admin
    template_name = "Admin (superusuario)/dashboard.html"

class CorredorDashboardView(TemplateView):
    # Esta ruta la usa tu JS para cargar el dashboard de corredor
    template_name = "Corredor/dashboard_corredor.html"

class SupervisorDashboardView(TemplateView):
    # Esta ruta la usa tu JS para cargar el dashboard de supervisor
    template_name = "Supervisor/dashboard_supervisor.html"