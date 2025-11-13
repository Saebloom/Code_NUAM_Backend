#!/bin/bash

echo "================================================="
echo " Script de Instalacion del Proyecto NUAM"
echo "================================================="

PYTHON_CMD="python3"

# 1. Revisa si Python 3 esta instalado
if ! command -v $PYTHON_CMD &> /dev/null
then
    echo "Error: '$PYTHON_CMD' no se encuentra."
    echo "Por favor, instala Python 3.12+."
    exit 1
fi

# 2. Crea el entorno virtual 'test'
echo ""
echo "[1/4] Creando entorno virtual 'test'..."
$PYTHON_CMD -m venv test
if [ $? -ne 0 ]; then
    echo "Error: No se pudo crear el entorno virtual."
    exit 1
fi

# 3. Instala las dependencias
echo ""
echo "[2/4] Instalando dependencias desde requirements.txt..."
test/bin/python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: No se pudieron instalar las dependencias."
    exit 1
fi

# 4. NUEVO: Configurar la base de datos MySQL
echo ""
echo "[3/4] Configurando la base de datos MySQL..."
echo "Por favor, ingresa tu contrasena de 'root' de MySQL:"
read -s MYSQL_ROOT_PASS # -s para modo silencioso

SQL_COMMANDS="CREATE DATABASE IF NOT EXISTS nuam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'nuamuser'@'localhost' IDENTIFIED BY 'NuamUser2025'; GRANT ALL PRIVILEGES ON nuam.* TO 'nuamuser'@'localhost'; FLUSH PRIVILEGES;"

mysql -u root -p"$MYSQL_ROOT_PASS" -e "$SQL_COMMANDS"

if [ $? -ne 0 ]; then
    echo "Error: No se pudo configurar la base de datos MySQL."
    echo "Asegurate de que MySQL este corriendo y la contrasena de root sea correcta."
    exit 1
fi
echo "Base de datos 'nuam' y usuario 'nuamuser' creados/verificados."

# 5. Ejecuta 'migrate' para crear la BD y los datos
echo ""
echo "[4/4] Creando tablas de Django y poblando datos iniciales..."
test/bin/python3 manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: Fallaron las migraciones."
    exit 1
fi

# 6. Exito
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