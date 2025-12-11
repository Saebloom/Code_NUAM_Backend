#!/bin/bash

echo "==========================================="
echo " 🚀 INICIANDO INSTALACIÓN EN LINUX/WSL"
echo "==========================================="

# --- 1. Validar Docker ---
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker no está instalado. Instálalo antes de continuar."
    exit 1
fi

echo "Docker encontrado ✔️"

# --- 2. Levantar contenedores ---
echo "Deteniendo contenedores previos..."
docker compose down

echo "Levantando stack Docker..."
docker compose up -d

echo "Esperando que MySQL del contenedor inicie..."
sleep 15

# --- 3. Migraciones ---
echo "Ejecutando migraciones..."
docker compose exec backend python manage.py migrate

# --- 4. Crear superusuario si no existe ---
echo "Creando superusuario automático (si no existe)..."
docker compose exec backend python manage.py createsuperuser --noinput || echo "(Ya existe)"

# --- 5. Estado final ---
echo "==========================================="
echo " 🎉 INSTALACIÓN COMPLETADA"
echo " Backend: http://localhost:8000"
echo " Kafka: localhost:9092"
echo " MySQL: localhost:3307"
echo "==========================================="
