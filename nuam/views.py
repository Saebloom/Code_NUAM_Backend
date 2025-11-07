from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout # Importa logout con alias

# Importa los modelos necesarios para las vistas de dashboard (asumiendo que están en la app 'api')
# Estado se incluye, aunque no se usa directamente en este código, se mantiene por si acaso.
from api.models import Calificacion, Log, Instrumento, Mercado, Estado 

# =============================================================
# VISTAS DE AUTENTICACIÓN Y LOGOUT
# =============================================================

def login_view(request):
    """Maneja el inicio de sesión y la redirección por rol."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 🔹 Redirige según el grupo o rol
            if user.is_superuser:
                return redirect("dashboard_admin")
            elif user.groups.filter(name="Supervisor").exists():
                return redirect("dashboard_supervisor")
            elif user.groups.filter(name="Corredor").exists():
                return redirect("dashboard_corredor")
            else:
                messages.warning(request, "Tu usuario no tiene un rol asignado.")
                return redirect("home")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect("home")
    
    # Manejo de GET (mostrar el formulario)
    return render(request, "index.html")

def logout_view(request):
    """Cierra la sesión y redirige al login."""
    django_logout(request)
    return redirect("home")

# Función auxiliar para obtener la URL de redirección del dashboard
def dashboard_selector(user):
    """Retorna la URL del dashboard correcta para el usuario."""
    if user.is_superuser:
        return reverse('dashboard_admin')
    
    if user.groups.filter(name='Supervisor').exists():
        return reverse('dashboard_supervisor')
    elif user.groups.filter(name='Corredor').exists():
        return reverse('dashboard_corredor')
    else:
        # En caso de no tener un rol definido, se puede elegir un dashboard por defecto.
        # Aquí se redirige al admin para que asigne un rol.
        return reverse('dashboard_admin')


# =============================================================
# VISTAS DE DASHBOARD (WEB/TEMPLATE)
# =============================================================

# 🔹 DASHBOARD ADMIN
@login_required
def dashboard_admin(request):
    """Vista del Dashboard para el Administrador (Superusuario)."""
    # Lógica para obtener datos relevantes (ejemplo)
    total_usuarios = request.user.__class__.objects.count()
    total_calificaciones = Calificacion.objects.count()
    total_logs = Log.objects.count()

    context = {
        'usuario': request.user,
        'total_usuarios': total_usuarios,
        'total_calificaciones': total_calificaciones,
        'total_logs': total_logs,
    }
    return render(request, 'Admin/dashboard.html', context)


# 🔹 DASHBOARD SUPERVISOR
@login_required
def dashboard_supervisor(request):
    """Vista del Dashboard para el Supervisor."""
    # Lógica para obtener datos relevantes (ejemplo)
    calificaciones = Calificacion.objects.all().order_by('-fecha_emision')
    logs = Log.objects.all().order_by('-fecha')[:50]

    context = {
        'usuario': request.user,
        'calificaciones': calificaciones,
        'logs': logs,
    }
    return render(request, 'Supervisor/dashboard_supervisor.html', context)


# 🔹 DASHBOARD CORREDOR
@login_required
def dashboard_corredor(request):
    """Vista del Dashboard para el Corredor."""
    # Lógica para obtener datos relevantes (ejemplo)
    # Solo las calificaciones del usuario
    calificaciones = Calificacion.objects.filter(usuario=request.user).order_by('-fecha_emision')

    # Instrumentos y mercados activos (asumiendo que el campo para el estado es 'nombre' o similar)
    # Esto puede requerir un ajuste si 'estado' no es un campo directo de Instrumento/Mercado
    instrumentos = Instrumento.objects.all() # Filtrar si es necesario
    mercados = Mercado.objects.all() # Filtrar si es necesario

    context = {
        'usuario': request.user,
        'calificaciones': calificaciones,
        'instrumentos': instrumentos,
        'mercados': mercados,
    }
    return render(request, 'Corredor/dashboard_corredor.html', context)