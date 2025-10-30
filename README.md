# 🚀 Proyecto NUAM TIHI43_V

Aplicación web desarrollada con **Django** y **Django REST Framework**, que incluye:

- Panel de administración (superusuario)
- API REST
- Templates HTML, CSS y JS
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

git clone https://github.com/Saebloom/Proyecto_NUAM_TIHI43_V.git

cd Proyecto_NUAM_TIHI43_V


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



---

## 👤 Crear superusuario (Admin)

### Método interactivo
python manage.py createsuperuser

Completa los datos solicitados:
Username: valeadmin
Email: vale@example.com

Password: ContraseñaSegura123!


### Método no interactivo (útil para scripts)

- **Windows PowerShell**
  
$env:DJANGO_SUPERUSER_USERNAME="valeadmin"

$env:DJANGO_SUPERUSER_EMAIL="vale@example.com"

$env:DJANGO_SUPERUSER_PASSWORD="ContraseñaSegura123!"

python manage.py createsuperuser --noinput


- **Linux / Mac bash**
  
export DJANGO_SUPERUSER_USERNAME=valeadmin

export DJANGO_SUPERUSER_EMAIL="vale@example.com"

export DJANGO_SUPERUSER_PASSWORD="ContraseñaSegura123!"

python manage.py createsuperuser --noinput


### Verificar admin

Abre el navegador en [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) e inicia sesión.

---

##Uso

- **Admin:** `/admin/` con superusuario  
- **Registro y login:** usuarios pueden registrarse con nombre, email y contraseña  
- **Publicación de retos:** solo superusuario o creador del reto puede publicar/eliminar  
- **Responder retos:** usuarios acumulan puntos por respuestas correctas  
- **Ranking:** top 10 usuarios por puntaje

---

## 📂 Estructura del proyecto📂 
Proyecto_NUAM_TIHI43_V/
├─ miapp/ # Aplicación principal (CRUD y API)
│ ├─ migrations/ # Migraciones
│ ├─ templates/ # Plantillas HTML
│ ├─ static/ # CSS, JS, imágenes
│ ├─ admin.py # Configuración del admin
│ ├─ models.py
│ ├─ views.py
│ └─ urls.py
├─ miweb/ # Configuración principal de Django
├─ templates/ # Templates globales
├─ manage.py
├─ db.sqlite3
├─ requirements.txt # Dependencias del proyecto
├─ setup.bat # Script Windows para instalar automáticamente
└─ README.md # Este archivo




---

##Dependencias

asgiref==3.9.2
Django==5.2.6
sqlparse==0.5.3
tzdata==2025.2
djangorestframework==3.15.2


> Se instalan automáticamente con:
pip install -r requirements.txt



---

## Notas importantes

- Base de datos: **SQLite** por defecto  
- Las migraciones deben generarse localmente (`makemigrations` + `migrate`)  
- Entorno virtual recomendado: `test`  
- Superusuario tiene permisos completos (`is_staff` e `is_superuser`)  
- Mantener `DEBUG=True` solo para desarrollo; en producción usar `DEBUG=False` y configurar `ALLOWED_HOSTS`

---


## Tips rápidos para editores

- Actualizar dependencias:

pip install <paquete>
pip freeze > requirements.txt



- Subir cambios a git:
git add .
git commit -m "Mensaje breve y claro"
git push origin main


- Levantar servidor:

python manage.py runserver

