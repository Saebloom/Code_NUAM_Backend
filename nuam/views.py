
from django.shortcuts import render, redirect # Solo se mantiene lo que se usa
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # Se usa para los dashboards
from django.contrib import messages # Se usa para mostrar mensajes de error/warning
from django.urls import reverse

# 🛑 ¡IMPORTANTE! Las líneas que causan el error deben ser corregidas
# para usar 'api' en lugar de 'nuam' o 'misma carpeta' si no corresponde:

# Si tu views.py principal necesita acceder a los Serializers:
# from api.serializers import CurrentUserSerializer # <-- Si fuera necesario usarlo aquí

# Si tu views.py principal necesita acceder a los Modelos:
from api.models import Calificacion, Log, Instrumento, Mercado, Estado # <-- Ejemplo de cómo debe ser el import

# -------------------------------------------------------------
# A CONTINUACIÓN, UNA VISTA WEB TÍPICA (LOGIN BASADO EN SESIÓN)
# -------------------------------------------------------------

def login_view(request):
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


# Función auxiliar para redirigir al dashboard correcto (basado en la lógica de rol de tu Serializer)
def dashboard_selector(user):
    if user.is_superuser:
        return reverse('dashboard_admin') # Asume que tienes una URL name 'dashboard_admin'
    
    # Lógica de rol basada en grupos (similar a tu CurrentUserSerializer)
    if user.groups.filter(name='Supervisor').exists():
        return reverse('dashboard_supervisor')
    elif user.groups.filter(name='Corredor').exists():
        return reverse('dashboard_corredor')
    else:
        # Si no tiene rol, quizás redirigir al admin para asignarlo
        return reverse('dashboard_admin')


@login_required
def dashboard_admin(request):
    # Esta es una vista web, no una API. Renderiza dashboard.html
    return render(request, 'templates/Admin/dashboard.html', {'usuario': request.user})

# ... y así sucesivamente para las otras vistas (supervisor, corredor) ...