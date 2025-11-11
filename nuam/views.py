# nuam/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import logout

def spa_entry(request):
    """ Sirve el index.html (Punto de entrada del SPA) """
    return render(request, "index.html")

def custom_logout_view(request):
    """ Maneja el logout y redirige al home (index.html) """
    logout(request)
    return redirect('home')

# Vistas de Template para los Dashboards (solo sirven el HTML)
class AdminDashboardView(TemplateView):
    template_name = "Admin (superusuario)/dashboard.html"

class CorredorDashboardView(TemplateView):
    template_name = "Corredor/dashboard_corredor.html"

class SupervisorDashboardView(TemplateView):
    template_name = "Supervisor/dashboard_supervisor.html"