# 🚀 Proyecto: Sistema de Calificaciones Tributarias (NUAM)

**Integrantes:**

  * Valeska Aguirre
  * Nicolas Espejo

Aplicación web desarrollada con **Django** y **Django REST Framework**, que incluye:

  * Panel de administración (Administrador)
  * Dashboard de Supervisión (Supervisor/Auditor)
  * Dashboard de Mantenedor (Corredor)
  * API REST con documentación Swagger
  * Sistema de Auditoría y Logs automáticos
  * Templates HTML, CSS y JS para cada rol
  * CRUD para usuarios y calificaciones tributarias
  * Carga Masiva (CSV/Excel) y Gestión de Respaldos

-----

## 🛠 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

  * Python 3.12 o superior
  * Git
  * **MySQL Server** (8.0 o superior, con el servicio `mysql` corriendo)
  * Navegador web (Chrome, Firefox, Edge)

> ⚠️ **Nota Importante:** Python y MySQL Server deben instalarse manualmente. No se pueden instalar automáticamente desde el proyecto.

## 🛠 Requisitos Previos (Específicos para Linux)
Para que el script de instalación automática (installinux.sh) funcione, el sistema (ej. Ubuntu/Debian) debe tener instaladas las siguientes dependencias de sistema.

Puedes instalarlas con los siguientes comandos:

# 1. Asegurar que Python 3.12, Git y el módulo Venv estén instalados
sudo apt update
sudo apt install git python3.12 python3.12-venv

# 2. Instalar el cliente de MySQL (para que el script pueda ejecutar comandos)
sudo apt install mysql-client

# 3. Instalar librerías de compilación (CRUCIAL)

sudo apt install build-essential python3.12-dev default-libmysqlclient-dev libffi-dev

-----

## ⚡ Instalación

Tienes dos formas de instalar el proyecto. La automática es la recomendada.

### Opción A: Instalación Automática (Recomendada)

Este método automatiza la creación del entorno, la instalación de paquetes y la configuración de la base de datos.

1.  Abre una terminal (CMD o PowerShell).

2.  Clona el repositorio y entra a la carpeta:

    
    git clone https://github.com/Saebloom/Code_NUAM_Backend.git
    
    cd Code_NUAM_Backend
  

3.  Asegúrate de que tu servicio MySQL Server se esté ejecutando en segundo plano.

4.  Ejecuta el script de instalación correspondiente:

      * **En Windows:**

          * Haz doble clic en el archivo `installwin.bat`.
          * O, desde tu terminal, escribe: `installwin.bat`

      * **En Linux / Mac:**

        1.  Otorga permisos de ejecución al script: `chmod +x installinux.

        2.  Ejecuta el script: ./installinux.sh

5.  **IMPORTANTE:** El script te pedirá tu contraseña de **`root` de MySQL**.

      * Esto es necesario para que el script pueda ejecutar automáticamente los comandos SQL para crear la base de datos `nuam` y el usuario `nuamuser`.

6.  Una vez que el script termine, activa el entorno virtual y levanta el servidor:

      * **En Windows:**

        1.  `test\Scripts\activate`
        2.  `python manage.py runserver`

      * **En Linux / Mac:**

        1.  `source test/bin/activate`
        2.  `python manage.py runserver`

-----

### Opción B: Instalación Manual (Paso a Paso)

Si la opción automática falla o prefieres un control total, sigue estos 5 pasos.

#### 1\. Clonar el Repositorio


git clone https://github.com/Saebloom/Code_NUAM_Backend.git

cd Code_NUAM_Backend


#### 2\. Crear y Activar Entorno Virtual

  * **Windows:**
    
    python -m venv test
    test\Scripts\activate
    
  * **Linux / Mac:**
    
    python3 -m venv test
    source test/bin/activate
    

#### 3\. Instalar Dependencias


pip install -r requirements.txt


#### 4\. Configurar la Base de Datos (Paso Manual de MySQL)

El proyecto está configurado en `settings.py` para buscar una base de datos MySQL específica. Debes crearla manualmente.

1.  Abre una terminal y conéctate a MySQL como `root`:
   
    mysql -u root -p
    
2.  Introduce tu contraseña de `root` de MySQL.
3.  Ejecuta los siguientes 3 comandos (uno por uno):
    
    CREATE DATABASE nuam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    
    
    CREATE USER 'nuamuser'@'localhost' IDENTIFIED BY 'NuamUser2025';
    
    
    GRANT ALL PRIVILEGES ON nuam.* TO 'nuamuser'@'localhost';
    
    EXIT;
    
    *Esto crea la base de datos `nuam` y le da al usuario `nuamuser` (definido en `settings.py`) todos los permisos sobre ella.*

#### 5\. Aplicar Migraciones y Ejecutar

1.  **Ejecuta `migrate`:** Este comando se conectará a la base de datos MySQL que acabas de crear, construirá todas las tablas y ejecutará los `signals` para crear los usuarios de prueba.
   
    python manage.py migrate
    
2.  **Ejecuta el servidor:**
    
    python manage.py runserver
   

-----

## 👤 Cuentas de Prueba (Creadas Automáticamente)

El proyecto **no** requiere que crees un superusuario manualmente. Estas 3 cuentas se crean automáticamente al ejecutar `migrate` (gracias al archivo `api/signals.py`):

| Rol | Correo | Contraseña |
| :--- | :--- | :--- |
| **Administrador** | `admin@nuam.cl` | `adminpass123` |
| **Supervisor** | `supervisor@nuam.cl` | `superpass123` |
| **Corredor** | `corredor@nuam.cl` | `correpass123` |

El sistema está disponible en **`http://127.0.0.1:8000/`**.

-----

## 🚀 Uso (Flujo de Roles)

El sistema opera bajo 3 roles principales. El acceso al login principal (`/`) redirigirá al dashboard correspondiente según el usuario.

  * **Administrador:**

      * Gestión de Usuarios y Roles.
      * Visualización de Logs/Auditoría completos.
      * Gestión de Respaldos del sistema.
      * Revisión del historial de Cargas Masivas.

  * **Supervisor (Auditor):**

      * Rol de solo lectura.
      * Consulta calificaciones registradas.
      * Accede a registros completos de operaciones (Historial).
      * Genera reportes consolidados (simulado).

  * **Corredor (Mantenedor):**

      * Rol de ingreso de datos.
      * Realiza el CRUD (Registrar, Modificar, Eliminar) de calificaciones.
      * Realiza Cargas Masivas vía archivos (CSV/Excel).
      * Visualización de su propio historial de operaciones.

-----

## 📂 Estructura del proyecto

```
Code_NUAM_Backend/
├─ api/         # App principal (models, views, serializers, signals)
├─ nuam/        # Configuración del proyecto (settings.py, urls.py)
├─ templates/   # Plantillas HTML (Admin, Corredor, Supervisor)
├─ static/      # CSS, JS, Imágenes
├─ logs/        # Archivos de log (ej. nuam.log)
├─ manage.py
├─ requirements.txt
├─ installwin.bat # Script de instalación Windows
├─ installinux.sh # Script de instalación Linux/Mac
├─ .gitignore
└─ README.md    # Este archivo
```

-----

## 📝 Notas Importantes

  * **Base de datos:** El proyecto está configurado para usar **MySQL**. La conexión está definida en `settings.py`. Los scripts de instalación (`installwin.bat`, `installinux.sh`) configuran esto automáticamente si proporcionas la contraseña de `root` correcta.
  * **Migraciones:** Solo necesitas ejecutar `python manage.py migrate`. No ejecutes `makemigrations` a menos que modifiques activamente los archivos `models.py`.
  * **Debug:** `DEBUG=True` está activado por defecto para desarrollo.
