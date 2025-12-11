# 1. Usamos Python ligero
FROM python:3.11-slim

# 2. Configuración para ver logs inmediatamente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Creamos la carpeta de trabajo
WORKDIR /app

# 4. Instalamos herramientas del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos los requerimientos e instalamos
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copiamos el resto del código
COPY . /app/

# 7. Comando por defecto (Mantiene el contenedor encendido)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]