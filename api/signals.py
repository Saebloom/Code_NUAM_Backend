# api/signals.py
import sys
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from .models import Instrumento, Mercado, Estado
from django.contrib.auth.models import Group
from django.conf import settings

# --- Contraseñas iniciales ---
ADMIN_PASS = 'adminpass123'
SUPER_PASS = 'superpass123'
CORRE_PASS = 'correpass123'

@receiver(post_migrate)
def setup_initial_data(sender, **kwargs):
    """
    Se ejecuta después de 'migrate'.
    Asegura que los grupos y los usuarios iniciales
    existan CON las contraseñas correctas.
    """
    # Solo se ejecuta cuando se migra la app 'api'
    if sender.name == 'api':
        # Evita que corra durante los tests
        if 'test' in sys.argv:
            return

        User = get_user_model()

        print("\n\n--- Ejecutando configuración inicial de datos (desde signals.py) ---")

        # 1. Crear Grupos
        grupo_supervisor, _ = Group.objects.get_or_create(name='Supervisor')
        grupo_corredor, _ = Group.objects.get_or_create(name='Corredor')
        print(" -> Grupos 'Supervisor' y 'Corredor' asegurados.")

        # 2. Crear/Actualizar Superusuario
        try:
            admin, created = User.objects.update_or_create(
                username='admin@nuam.cl',
                defaults={
                    'email': 'admin@nuam.cl', 'first_name': 'Admin',
                    'is_staff': True, 'is_superuser': True
                }
            )
            if created:
                admin.set_password(ADMIN_PASS)
                admin.save()
                print(" -> Superusuario 'admin@nuam.cl' CREADO.")
            else:
                print(" -> Superusuario 'admin@nuam.cl' ya existía.")
                
        except Exception as e:
            print(f" ERROR creando admin: {e}")


        # 3. Crear/Actualizar Supervisor
        user_sup, created = User.objects.update_or_create(
            username='supervisor@nuam.cl',
            defaults={
                'email': 'supervisor@nuam.cl', 'first_name': 'Supervisor',
                'last_name': 'NUAM', 'is_active': True,
                'is_staff': False, 'is_superuser': False
            }
        )
        if created:
            user_sup.set_password(SUPER_PASS) # Seteamos la contraseña
            user_sup.groups.set([grupo_supervisor]) # Asignamos el grupo
            user_sup.save()
            print(" -> Usuario 'supervisor@nuam.cl' CREADO.")
        else:
             print(" -> Usuario 'supervisor@nuam.cl' ya existía.")


        # 4. Crear/Actualizar Corredor
        user_cor, created = User.objects.update_or_create(
            username='corredor@nuam.cl',
            defaults={
                'email': 'corredor@nuam.cl', 'first_name': 'Corredor',
                'last_name': 'NUAM', 'is_active': True,
                'is_staff': False, 'is_superuser': False
            }
        )
        if created:
            user_cor.set_password(CORRE_PASS) # Seteamos la contraseña
            user_cor.groups.set([grupo_corredor]) # Asignamos el grupo
            user_cor.save()
            print(" -> Usuario 'corredor@nuam.cl' CREADO.")
        else:
            print(" -> Usuario 'corredor@nuam.cl' ya existía.")

        print(" -> Asegurando datos iniciales (Estado, Mercado, Instrumento)...")
        
        # --- Estados (Estos son genéricos) ---
        Estado.objects.update_or_create(id=1, defaults={'nombre': 'Validado'})
        Estado.objects.update_or_create(id=2, defaults={'nombre': 'Pendiente'})
        Estado.objects.update_or_create(id=3, defaults={'nombre': 'Rechazado'})
        
        # --- Mercados (Solo CL, CO, PE) ---
        Mercado.objects.update_or_create(
            id=1, defaults={'nombre': 'Mercado Chile (CL)', 'pais': 'CL', 'tipo': 'Bursátil'}
        )
        Mercado.objects.update_or_create(
            id=2, defaults={'nombre': 'Mercado Colombia (CO)', 'pais': 'CO', 'tipo': 'Bursátil'}
        )
        Mercado.objects.update_or_create(
            id=3, defaults={'nombre': 'Mercado Perú (PE)', 'pais': 'PE', 'tipo': 'Bursátil'}
        )
        
        # --- Instrumentos (5 ejemplos de CL, CO, PE) ---
        Instrumento.objects.update_or_create(
            id=1, defaults={'nombre': 'Bono Soberano (CL)', 'tipo': 'Bono', 'moneda': 'CLP'}
        )
        Instrumento.objects.update_or_create(
            id=2, defaults={'nombre': 'Acción COPEC (CL)', 'tipo': 'Acción', 'moneda': 'CLP'}
        )
        Instrumento.objects.update_or_create(
            id=3, defaults={'nombre': 'Bono Ecopetrol (CO)', 'tipo': 'Bono', 'moneda': 'COP'}
        )
        Instrumento.objects.update_or_create(
            id=4, defaults={'nombre': 'Acción Intercorp (PE)', 'tipo': 'Acción', 'moneda': 'PEN'}
        )
        Instrumento.objects.update_or_create(
            id=5, defaults={'nombre': 'Fondo Mutuo LATAM (CL)', 'tipo': 'Fondo', 'moneda': 'CLP'}
        )
        
        print(" -> Datos iniciales (CL, CO, PE) creados/actualizados.")
        


        print("--- Configuración inicial terminada ---\n")

# --- NO AGREGUES NINGÚN OTRO CÓDIGO A ESTE ARCHIVO ---