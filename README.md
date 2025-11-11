# 🚀 Proyecto: Sistema de Calificaciones Tributarias (TIHI43)

Aplicación web desarrollada con **Django** y **Django REST Framework**, que incluye:

* Panel de administración (Administrador)
* Dashboard de Supervisión (Supervisor/Auditor)
* Dashboard de Mantenedor (Corredor)
* API REST con documentación Swagger
* Sistema de Auditoría y Logs automáticos
* Templates HTML, CSS y JS para cada rol
* CRUD para usuarios y calificaciones tributarias
* Carga Masiva (CSV) y Gestión de Respaldos

---

## 🛠 Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

* Python 3.12 o superior
* Git
* Servidor MySQL (para la base de datos)
* Navegador web (Chrome, Firefox, Edge)

> ⚠️ Python y MySQL deben instalarse manualmente. No se pueden instalar automáticamente desde el proyecto.

---

## ⚡ Instalación

### 1. Clonar el repositorio

Clona el repositorio y entra a la carpeta:

git clone [https://github.com/Saebloom/Code_NUAM_Backend.git](https://github.com/Saebloom/Code_NUAM_Backend.git)
cd Code_NUAM_Backend

### 2.Crear y activar entorno virtual
#### Windows

python -m venv test

test\Scripts\activate


#### Linux / Mac

python3 -m venv test

source test/bin/activate

### 3. Instalar dependencias

pip install -r requirements.txt


Nota: Este proyecto utiliza MySQL. Asegúrate de tener mysqlclient instalado y de configurar tu conexión local en settings.py o un archivo .env.


### 4. Aplicar migraciones

python manage.py makemigrations

python manage.py migrate

### 5. Ejecutar servidor de desarrollo

python manage.py runserver

## 👤 Crear superusuario (Admin)

python manage.py createsuperuser

Username: admin

Email: admin@nuam.cl

Password: Administrador.2025

(El email debe ser válido según la configuración del proyecto).


## Método no interactivo (útil para scripts)
### Windows PowerShell

$env:DJANGO_SUPERUSER_USERNAME="admin"

$env:DJANGO_SUPERUSER_EMAIL="admin@example.com"

$env:DJANGO_SUPERUSER_PASSWORD="Administrador.2025"

python manage.py createsuperuser --noinput

### Linux / Mac (bash)

export DJANGO_SUPERUSER_USERNAME=admin

export DJANGO_SUPERUSER_EMAIL="admin@example.com"

export DJANGO_SUPERUSER_PASSWORD="Administrador.2025"

python manage.py createsuperuser --noinput


# 🚀 Uso (Flujo de Roles)
El sistema opera bajo 3 roles principales. El acceso al login principal (/) redirigirá al dashboard correspondiente según el usuario.

### Administrador:

-Gestión de Usuarios y Roles (CRUD).

-Visualización de Logs/Auditoría completos.

-Gestión de Respaldos del sistema.

-Revisión del historial de Cargas Masivas.

### Supervisor (Auditor):

-Rol de solo lectura.

-Consulta calificaciones registradas.

-Accede a registros completos de operaciones (Historial).

-Genera reportes consolidados.

### Corredor (Mantenedor):

-Rol de ingreso de datos.

-Realiza el CRUD (Registrar, Modificar, Eliminar) de calificaciones.

-Realiza Cargas Masivas vía archivos CSV.

-Visualización de su propio historial de operaciones.

# 📂 Estructura del proyecto 📂

Code_NUAM_Backend/
├─ api/         # App principal (models, views, serializers, signals)
├─ nuam/        # Configuración del proyecto (settings.py, urls.py)
├─ templates/   # Plantillas HTML (Admin, Corredor, Supervisor)
├─ static/      # CSS, JS, Imágenes
├─ logs/        # Archivos de log (ej. nuam.log)
├─ manage.py
├─ db.sqlite3   # (Solo para desarrollo inicial, la BD principal es MySQL)
├─ requirements.txt
├─ .gitignore
└─ README.md    # Este archivo 

# 📦 Dependencias 

#### ---Se instalan automáticamente con: pip install -r requirements.txt ---
asgiref==3.9.2
Django==5.2.6
django-cors-headers==4.9.0
django-jazzmin==3.0.1
djangorestframework==3.15.2
djangorestframework_simplejwt==5.5.1
drf-yasg==1.21.11
inflection==0.5.1
packaging==25.0
PyJWT==2.10.1
pytz==2025.2
PyYAML==6.0.3
sqlparse==0.5.3
typing_extensions==4.15.0
tzdata==2025.2
uritemplate==4.2.0



# ✨ Tips rápidos para editores
### Actualizar dependencias:

pip install <paquete>

### Subir cambios a git:
git add .

git commit -m "Mensaje breve y claro"

git push origin main

pip freeze > requirements.txt

### Levantar servidor:

python manage.py runserver


# 📝 Notas importantes
-Base de datos: El proyecto está diseñado para MySQL.

- Migraciones: Deben generarse y aplicarse localmente (makemigrations + migrate).

- Entorno virtual: Se recomienda usar un entorno virtual (test, venv, etc.).

- Superusuario: Tiene permisos completos (is_staff e is_superuser).

- Debug: Mantener DEBUG=True solo para desarrollo; en producción usar DEBUG=False y configurar ALLOWED_HOSTS.

