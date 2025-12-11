#!/bin/bash

COMMAND=$1

if [ -z "$COMMAND" ]; then
    echo
    echo "Uso: ./compose-helper.sh <comando>"
    echo
    echo "Comandos disponibles:"
    echo "  up              - Levanta servicios"
    echo "  down            - Detiene servicios"
    echo "  logs            - Logs del backend"
    echo "  bash            - Ingresa al contenedor backend"
    echo "  mysql           - Ingresa al MySQL del contenedor"
    echo "  migrate         - Ejecuta migraciones"
    echo "  makemigrations  - Crea nuevas migraciones"
    echo "  rebuild         - Reconstruye imagen del backend"
    echo
    exit 0
fi

case $COMMAND in
    up) docker compose up -d ;;
    down) docker compose down ;;
    logs) docker compose logs -f backend ;;
    bash) docker compose exec backend bash ;;
    mysql) docker compose exec db mysql -u root -prootpassword ;;
    migrate) docker compose exec backend python manage.py migrate ;;
    makemigrations) docker compose exec backend python manage.py makemigrations ;;
    rebuild) docker compose up -d --build ;;
    *)
        echo "Comando no reconocido: $COMMAND"
        exit 1
        ;;
esac
