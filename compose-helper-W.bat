@echo off
set COMMAND=%1

if "%COMMAND%"=="" (
    echo.
    echo Uso: compose-helper.bat ^<comando^>
    echo.
    echo Comandos disponibles:
    echo   up            - Levanta el sistema (start)
    echo   down          - Apaga el sistema (stop)
    echo   logs          - Ver que esta pasando en el backend (logs)
    echo   bash          - Entrar a la terminal del Linux (backend)
    echo   mysql         - Entrar a la base de datos SQL
    echo   migrate       - Aplicar cambios de base de datos
    echo   test          - Ejecutar pruebas unitarias
    echo.
    exit /b
)

if "%COMMAND%"=="up" docker compose up -d
if "%COMMAND%"=="down" docker compose down
if "%COMMAND%"=="logs" docker compose logs -f backend
if "%COMMAND%"=="bash" docker compose exec backend bash
REM Nota: La password aca debe coincidir con tu docker-compose.yml
if "%COMMAND%"=="mysql" docker compose exec db mysql -u root -prootpassword nuam_db
if "%COMMAND%"=="migrate" docker compose exec backend python manage.py migrate
if "%COMMAND%"=="test" docker compose exec backend python manage.py test

echo.
echo Comando ejecutado.