# 🚀 Proyecto NUAM TIHI43_V

Aplicación web desarrollada con **Django** y **Django REST Framework**, que incluye:

- Panel de administración (superusuario)
- API REST
- Requerimientos y dependencias
- Templates HTML, CSS y JS (como SPA)
- CRUD para usuarios y contenidos

---

## 🛠 Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.12 o superior  
- Git  
- Navegador web (Chrome, Firefox, Edge)  

> ⚠️ Python debe instalarse manualmente. No se puede instalar automáticamente desde el proyecto.

---

## ⚡ Instalación

### 1. Clonar el repositorio

Clona el repositorio y entra a la carpeta:

git clone https://github.com/Saebloom/Code_NUAM_Backend.git

cd Code_NUAM_Backend


### 2. Crear y activar entorno virtual

- **Windows**

python -m venv test

test\Scripts\activate

- **Linux / Mac**
python3 -m venv test

source test/bin/activate


### 3. Instalar dependencias
pip install -r requirements.txt

### 4. Aplicar migraciones
python manage.py makemigrations

python manage.py migrate

### 5. Ejecutar servidor de desarrollo:
python manage.py runserver

Luego abre tu navegador en http://127.0.0.1:8000/

---

## 👤 Crear superusuario (Admin)

### Método interactivo
python manage.py createsuperuser

Completa los datos solicitados:

Username: admin@nuam.cl (Usa un email corporativo)
Email: admin@nuam.cl
Password: ContraseñaSegura123!

### Verificar admin

Abre el navegador en [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) e inicia sesión.

---

## 📂 Estructura del proyecto 📂 

Proyecto_NUAM/
├─ api/ # Aplicación principal (CRUD y API)
│ ├─ migrations/
│ ├─ admin.py # Configuración del admin
│ ├─ models.py
│ ├─ views.py
│ ├─ serializers.py
│ ├─ signals.py
│ └─ urls.py
├─ nuam/ # Configuración principal de Django
│ ├─ settings.py
│ ├─ urls.py
│ ├─ views.py
│ ├─ wsgi.py
│ └─ asgi.py
├─ templates/ # Templates HTML (SPA y sitio Django)
│ ├─ Admin/
│ ├─ Corredor/
│ ├─ Supervisor/
│ └─ index.html
├─ static/ # CSS, JS, imágenes
├─ manage.py
├─ db.sqlite3
├─ requirements.txt # Dependencias del proyecto
└─ README.md # Este archivo

---

## Dependencias

(Contenido de requirements.txt)

> Se instalan automáticamente con:
pip install -r requirements.txt

---

## Notas importantes

- Base de datos: **SQLite** por defecto.
- Entorno virtual recomendado: `test`.
- Superusuario tiene permisos completos (`is_staff` e `is_superuser`).
- Mantener `DEBUG=True` solo para desarrollo.