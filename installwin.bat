@echo off
echo =================================================
echo  Script de Instalacion del Proyecto NUAM
echo =================================================

:: (El README menciona 'python' para Windows)
set PYTHON_CMD=python

:: 1. Revisa si Python esta instalado
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: 'python' no se encuentra.
    echo Por favor, instala Python 3.12+ y asegurate de que este en el PATH.
    pause
    exit /b 1
)

:: 2. Crea el entorno virtual 'test' (como dice el README)
echo.
echo [1/3] Creando entorno virtual 'test'...
%PYTHON_CMD% -m venv test

if %errorlevel% neq 0 (
    echo Error: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

:: 3. Instala las dependencias (SIN activar, llamando a pip directamente)
echo.
echo [2/3] Instalando dependencias desde requirements.txt...
call test\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

:: 4. Ejecuta 'migrate' para crear la BD y los datos
echo.
echo [3/3] Creando la base de datos y poblando datos iniciales...
call test\Scripts\python.exe manage.py migrate

if %errorlevel% neq 0 (
    echo Error: Fallaron las migraciones.
    pause
    exit /b 1
)

:: 5. Exito
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