@echo off
echo =================================================
echo  Script de Instalacion del Proyecto NUAM
echo =================================================

set PYTHON_CMD=python

:: 1. Revisa si Python esta instalado
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: 'python' no se encuentra.
    echo Por favor, instala Python 3.12+ y asegurate de que este en el PATH.
    pause
    exit /b 1
)

:: 2. Crea el entorno virtual 'test'
echo.
echo [1/4] Creando entorno virtual 'test'...
%PYTHON_CMD% -m venv test
if %errorlevel% neq 0 (
    echo Error: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

:: 3. Instala las dependencias
echo.
echo [2/4] Instalando dependencias desde requirements.txt...
call test\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

:: 4. NUEVO: Configurar la base de datos MySQL
echo.
echo [3/4] Configurando la base de datos MySQL...
echo.
echo Por favor, ingresa tu contrasena de 'root' de MySQL (la que usas para Workbench):
set /p MYSQL_ROOT_PASS=Contrasena: 

set "SQL_COMMANDS=CREATE DATABASE IF NOT EXISTS nuam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'nuamuser'@'localhost' IDENTIFIED BY 'NuamUser2025'; GRANT ALL PRIVILEGES ON nuam.* TO 'nuamuser'@'localhost'; FLUSH PRIVILEGES;"

:: Asumimos que 'mysql' está en el PATH del sistema
mysql -u root -p%MYSQL_ROOT_PASS% -e "%SQL_COMMANDS%"

if %errorlevel% neq 0 (
    echo.
    echo :: ERROR ::
    echo No se pudo configurar la base de datos MySQL.
    echo Asegurate de que MySQL este corriendo y la contrasena de root sea correcta.
    pause
    exit /b 1
)
echo Base de datos 'nuam' y usuario 'nuamuser' creados/verificados.

:: 5. Ejecuta 'migrate' para crear la BD y los datos
echo.
echo [4/4] Creando tablas de Django y poblando datos iniciales...
call test\Scripts\python.exe manage.py migrate
if %errorlevel% neq 0 (
    echo Error: Fallaron las migraciones.
    pause
    exit /b 1
)

:: 6. Exito
echo.
echo =======================================================
echo   Instalacion completada con exito!
echo =======================================================
echo.
echo Para iniciar el servidor, ejecuta los siguientes comandos:
echo.
echo   1. test\Scripts\activate
echo   2. python manage.py runserver
echo.
pause