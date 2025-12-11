@echo off
@chcp 65001 >nul
echo ===========================================
echo 🚀 INICIANDO INSTALACION DEL PROYECTO NUAM
echo ===========================================

REM --- 1. Validar Docker (Motor Encendido) ---
echo [1/5] Verificando que Docker Desktop este corriendo...
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR CRITICO: Docker Desktop no esta corriendo.
    echo.
    echo POR FAVOR:
    echo 1. Busca "Docker Desktop" en Inicio y abrelo.
    echo 2. Espera a que el icono de la ballena se ponga verde.
    echo 3. Vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b
)

REM --- 2. Levantar contenedores ---
echo [2/5] Reiniciando contenedores (Clean Start)...
docker compose down
echo Levantando servicios...
docker compose up -d --build

REM --- Truco de espera universal (Ping a localhost por 15 segs) ---
echo [3/5] Esperando a que la Base de Datos inicie (15 seg)...
ping -n 16 127.0.0.1 >nul

REM --- 3. Migraciones ---
echo [4/5] Ejecutando migraciones de Base de Datos...
docker compose exec backend python manage.py migrate

REM --- 4. Crear superusuario fijo ---
echo [5/5] Creando superusuario 'admin' (Pass: admin123)...
docker compose exec -e DJANGO_SUPERUSER_PASSWORD=admin123 -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_EMAIL=admin@nuam.cl backend python manage.py createsuperuser --noinput || echo (El usuario admin ya existe, omitiendo...)

REM --- 5. Estado final ---
echo ===========================================
echo 🎉 INSTALACION COMPLETADA EXITOSAMENTE
echo ===========================================
echo 🌍 Backend HTTPS: https://localhost:8000
echo 👤 Superusuario:  admin / admin123
echo 📨 Kafka Broker:  localhost:9092
echo 🗄️  MySQL DB:     localhost:3307
echo ===========================================
pause