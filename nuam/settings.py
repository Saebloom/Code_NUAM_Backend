import os
from pathlib import Path
from datetime import timedelta
import pymysql

# --- Configuración Inicial de MySQL ---
# Esto permite que Django use pymysql como si fuera el cliente nativo
pymysql.install_as_MySQLdb()

# Construye rutas dentro del proyecto: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURIDAD: Mejor usar variables de entorno en producción
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-clave-secreta-para-desarrollo-nuam")

# DEBUG: True para ver errores detallados en desarrollo
DEBUG = True

# Permitimos todos los hosts para evitar problemas con Docker
ALLOWED_HOSTS = ["*"]


# ------------------------------------------------------------------------------
# APLICACIONES INSTALADAS
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'sslserver',                    # <--- IMPORTANTE: Debe ir primero para HTTPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Librerías de Terceros
    'corsheaders',                  # Para permitir peticiones del frontend
    'rest_framework',               # Django Rest Framework (DRF)
    'rest_framework_simplejwt',     # Autenticación JWT
    'drf_yasg',                     # Documentación Swagger
    
    # Tus Apps
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # <--- Debe ir lo más arriba posible
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nuam.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Asegúrate de tener esta carpeta creada
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nuam.wsgi.application'


# ------------------------------------------------------------------------------
# BASE DE DATOS (Configuración Híbrida Docker/Local)
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'nuam_db'),
        'USER': os.environ.get('DB_USER', 'nuam_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password123'),
        # Si estamos en Docker, el host es 'db'. Si no, es '127.0.0.1'
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}


# ------------------------------------------------------------------------------
# USUARIO PERSONALIZADO
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = 'api.Usuario'

# Validaciones de contraseña (puedes relajarlas para desarrollo)
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ------------------------------------------------------------------------------
# INTERNACIONALIZACIÓN
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, Images)
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Donde se recolectan al hacer collectstatic

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------------------------------------------------------
# DJANGO REST FRAMEWORK + JWT
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # Por defecto todo privado
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Configuración para que Swagger sepa usar el JWT
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
}


# ------------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing)
# ------------------------------------------------------------------------------
# En desarrollo permitimos todo para evitar dolores de cabeza
CORS_ALLOW_ALL_ORIGINS = True 

# Si quisieras ser estricta, usa esto:
# CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS = [
#     "https://localhost:8000",
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
# ]


# ------------------------------------------------------------------------------
# LOGGING (Para ver errores en la consola de Docker)
# ------------------------------------------------------------------------------
LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'nuam.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# En producción esto debe ser True, pero con runsslserver en Docker lo simulamos
SECURE_SSL_REDIRECT = False # Lo maneja runsslserver localmente
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# --- CONFIGURACIÓN KAFKA ---
import os
KAFKA_SERVER = os.environ.get('KAFKA_SERVER', 'localhost:9092')

# Redirecciones de Login
LOGIN_URL = "/"
LOGOUT_REDIRECT_URL = "/"