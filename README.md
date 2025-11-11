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
* Navegador web (Chrome, Firefox, Edge)

> ⚠️ Python debe instalarse manually. No se puede instalar automáticamente desde el proyecto.

---

## ⚡ Instalación

    Tienes dos formas de instalar el proyecto. La automática es la recomendada.

    ### Opción A: Instalación Automática (Recomendada)
    
    abrir cmd

    Clona el repositorio y entra a la carpeta:
    ```bash
    git clone [https://github.com/Saebloom/Code_NUAM_Backend.git](https://github.com/Saebloom/Code_NUAM_Backend.git)
    cd Code_NUAM_Backend
    ```

    Usa los scripts de instalación que preparan todo el entorno automáticamente.

    * **En Windows:**
        1.  Haz doble clic en el archivo `install.bat`.
        2.  Espera a que la terminal termine de instalar todo.

    * **En Linux / Mac:**
        1.  Otorga permisos de ejecución al script: `chmod +x install.sh`
        2.  Ejecuta el script: `./install.sh`

    Estos scripts crearán el entorno virtual `test/`, instalarán las dependencias y ejecutarán `migrate` para configurar la base de datos y crear los usuarios de prueba.

### Opción B: Forma manual

abrir cmd

Clona el repositorio y entra a la carpeta:

git clone [https://github.com/Saebloom/Code_NUAM_Backend.git](https://github.com/Saebloom/Code_NUAM_Backend.git)
cd Code_NUAM_Backend

### 2.Crear y activar entorno virtual
Windows

python -m venv test

test\Scripts\activate


Linux / Mac
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
---

## 👤 Cuentas de Prueba (Creadas Automáticamente)

El proyecto **no** requiere que crees un superusuario manualmente. Se crean 3 usuarios por defecto al ejecutar `migrate`:

| Rol | Correo | Contraseña |
| :--- | :--- | :--- |
| **Administrador** | `admin@nuam.cl` | `adminpass123` |
| **Supervisor** | `supervisor@nuam.cl` | `superpass123` |
| **Corredor** | `corredor@nuam.cl` | `correpass123` |

---

## 🚀 Ejecutar servidor de desarrollo

Después de la instalación (automática o manual), asegúrate de tener el entorno virtual activado y ejecuta:

```bash
# (Si no está activado) test\Scripts\activate
python manage.py runserver
El sistema estará disponible en http://127.0.0.1:8000/.

🚀 Uso (Flujo de Roles)
El sistema opera bajo 3 roles principales. El acceso al login principal (/) redirigirá al dashboard correspondiente según el usuario.

Administrador:
Gestión de Usuarios y Roles.

Visualización de Logs/Auditoría completos.

Gestión de Respaldos del sistema.

Revisión del historial de Cargas Masivas.

Supervisor (Auditor):
Rol de solo lectura.

Consulta calificaciones registradas.

Accede a registros completos de operaciones (Historial).

Genera reportes consolidados.

Corredor (Mantenedor):
Rol de ingreso de datos.

Realiza el CRUD (Registrar, Modificar, Eliminar) de calificaciones.

Realiza Cargas Masivas vía archivos CSV.

Visualización de su propio historial de operaciones.

📂 Estructura del proyecto 📂
Code_NUAM_Backend/
├─ api/         # App principal (models, views, serializers, signals)
├─ nuam/        # Configuración del proyecto (settings.py, urls.py)
├─ templates/   # Plantillas HTML (Admin, Corredor, Supervisor)
├─ static/      # CSS, JS, Imágenes
├─ logs/        # Archivos de log (ej. nuam.log)
├─ manage.py
├─ requirements.txt
├─ install.bat  # Script de instalación Windows
├─ install.sh   # Script de instalación Linux/Mac
├─ .gitignore
└─ README.md    # Este archivo
📝 Notas importantes
Base de datos: El proyecto usa SQLite por defecto. La base de datos (db.sqlite3) se crea y configura automáticamente con migrate.

Migraciones: Solo necesitas ejecutar python manage.py migrate. No ejecutes makemigrations a menos que modifiques activamente los archivos models.py.

Debug: DEBUG=True está activado por defecto para desarrollo.