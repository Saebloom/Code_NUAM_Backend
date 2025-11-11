#!/bin/bash

echo "================================================="
echo " Script de Instalacion del Proyecto NUAM"
echo "================================================="

# (El README menciona 'python3' para Linux/Mac)
PYTHON_CMD="python3"

# 1. Revisa si Python 3 esta instalado
if ! command -v $PYTHON_CMD &> /dev/null
then
    echo "Error: '$PYTHON_CMD' no se encuentra."
    echo "Por favor, instala Python 3.12+."
    exit 1
fi

# 2. Crea el entorno virtual 'test' (como dice el README)
echo ""
echo "[1/3] Creando entorno virtual 'test'..."
$PYTHON_CMD -m venv test

if [ $? -ne 0 ]; then
    echo "Error: No se pudo crear el entorno virtual."
    exit 1
fi

# 3. Instala las dependencias (SIN activar, llamando a pip directamente)
echo ""
echo "[2/3] Instalando dependencias desde requirements.txt..."
test/bin/python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: No se pudieron instalar las dependencias."
    exit 1
fi

# 4. Ejecuta 'migrate' para crear la BD y los datos
echo ""
echo "[3/3] Creando la base de datos y poblando datos iniciales..."
test/bin/python3 manage.py migrate

if [ $? -ne 0 ]; then
    echo "Error: Fallaron las migraciones."
    exit 1
fi

# 5. Exito
echo ""
echo "======================================================="
echo "  Instalacion completada con exito!"
echo "======================================================="
echo ""
echo "Para iniciar el servidor, ejecuta los siguientes comandos:"
echo ""
echo "  1. source test/bin/activate"
echo "  2. python manage.py runserver"
echo ""