# 🚀 Proyecto: Sistema de Calificaciones Tributarias (NUAM)
**Integrantes del Equipo**

* **Valeska Aguirre** Consumer, Microservicios, Base de Datos, Modelos.

* **Nicolás Espejo** Productores (Kafka), HTTPS, API RESTful, Arquitectura.

### ✨ Descripción del Proyecto: Aplicación web empresarial desarrollada con Django y Docker, diseñada bajo una arquitectura de microservicios y eventos.

### Características Principales:

* **Seguridad End-to-End: Protocolo HTTPS forzado con manejo de cookies seguras (SSL/TLS).**

* **Arquitectura Orientada a Eventos: Integración real con Apache Kafka (Productores y Consumidores).**

* **API RESTful: Endpoints estandarizados con documentación automática (Swagger).**

* **Roles Diferenciados: Dashboards para Administrador, Supervisor y Corredor.**

* **Integridad de Datos: Validaciones transaccionales y Carga Masiva (Excel/CSV).**

##  🛠 1. Requisitos Previos
La arquitectura actual está contenerizada. No necesitas instalar Python ni MySQL en tu máquina local, todo se ejecuta dentro de Docker.

Solo necesitas:

Docker Desktop: Debe estar actualizado y en ejecución (En Windows, asegúrate de tener WSL2 activado).

Git: Para clonar el repositorio.

Navegador Web: Edge, Chrome o Firefox.

## ⚡ 2. Instalación y Despliegue
## Paso 1: Clonar el repositorio Ejecuta el siguiente comando en tu terminal: git clone https://github.com/Saebloom/Code_NUAM_Backend.git cd Code_NUAM_Backend

## Paso 2: Ejecutar Script de Instalación Hemos automatizado todo el despliegue (Base de datos, Kafka, Certificados SSL y Backend).

## En Windows: Haz doble clic en el archivo install_windows.bat o ejecútalo desde la terminal.

## En Linux / Mac: Otorga permisos (chmod +x install_linux.sh) y ejecuta ./install_linux.sh.

⏳ Nota: La primera vez puede tardar unos minutos en descargar las imágenes de Docker y levantar Kafka. El script intentará crear automáticamente los usuarios base.

## 3. Paso Crítico: Acceso HTTPS (Certificado SSL)
Para cumplir con los estándares de seguridad exigidos, el sistema usa HTTPS. Como utilizamos un certificado de desarrollo generado localmente ("autofirmado"), el navegador mostrará una advertencia la primera vez.

## Debes autorizar el certificado manualmente:

* **Intenta acceder a: https://localhost:8000/admin/**

Verás una pantalla roja o gris de advertencia ("La conexión no es privada" o "No seguro").

Haz clic en el botón "Configuración Avanzada" (o "Más información").

## Haz clic en el enlace inferior que dice: "Continuar a localhost (no seguro)".

Una vez veas el inicio de sesión azul de Django, el navegador ya confía en el sitio.

Ya puedes acceder al inicio del sistema en: https://localhost:8000/

## 4. Credenciales de Acceso
El sistema crea automáticamente estos usuarios al iniciar:

* **Administrador**

Usuario: admin@nuam.cl

Contraseña: adminpass123

Función: Gestión total, Usuarios, Backups y Logs.

* **Supervisor**

Usuario: supervisor@nuam.cl

Contraseña: superpass123

Función: Auditoría, Reportes y Consulta Global.

* **Corredor**

Usuario: corredor@nuam.cl

Contraseña: correpass123

Función: Carga Masiva, Registro Manual, Productores Kafka.

## 5. 🔗 Endpoints del Sistema
Debido a la seguridad SSL, asegúrate de usar siempre el protocolo https://.

* **Frontend (Login y Dashboards): https://localhost:8000/**

* **Documentación API (Swagger): https://localhost:8000/swagger/**

* **Admin Panel (Backend): https://localhost:8000/admin/**

## 6. 🏗️ Arquitectura Técnica
El proyecto se ejecuta sobre 4 contenedores orquestados en Docker:

Backend (Django + Gunicorn + SSL): Expone el puerto 8000. Maneja la lógica de negocio, Productores Kafka y API REST.

Kafka (Message Broker):

Puerto Interno: 29092 (Comunicación con Django).

Puerto Externo: 9092 (Monitoreo).

Zookeeper: Coordinador del clúster Kafka.

MySQL 8.0: Persistencia de datos relacional (Puerto 3307).

Detalle de Responsabilidades:

Productores Kafka: Implementados en el módulo api/producers.py. Se activan al crear calificaciones en el ViewSet.

Seguridad HTTPS: Implementada mediante django-sslserver y certificados X.509 (cert.pem, key.pem).

API RESTful: Uso estricto de ModelViewSet y DefaultRouter en api/views.py.

Manejo de Errores: Bloques try/except transaccionales para cargas masivas y conexión a Kafka.

## 7. 🆘 Solución de Problemas Comunes
* **Problema 1: El navegador dice "No seguro" en rojo. Es normal en un entorno local (localhost). El tráfico sí está encriptado. Solo debes aceptar la excepción de seguridad como se indicó en la sección 3.**

* **Problema 2: Error "Connection refused" en Kafka. Asegúrate de que los contenedores estén corriendo ejecutando docker compose ps en la terminal. Si Kafka está detenido ("Exited"), reinícialo con el comando: docker compose restart zookeeper kafka.**

* **Problema 3: No puedo iniciar sesión (Error de red). Verifica que estás usando https:// y no http://. El servidor está configurado para rechazar conexiones inseguras.**