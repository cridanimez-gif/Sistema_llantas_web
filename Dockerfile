# ==============================================
# 1. IMAGEN BASE DE PYTHON
# ==============================================

# Indica que utilizaremos Python 3.14 como base para ejecutar nuestro proyecto Django.
FROM python:3.14-slim

# ==============================================
# 2. CONFIGURACIÓN DE PYTHON
# ==============================================

# Evita que Python almacene archivos temporales de bytecode (.pyc) dentro del proyecto.
ENV PYTHONDONTWRITEBYTECODE=1

# Permite que los mensajes de Python aparezcan directamente en los registros del contenedor.
ENV PYTHONUNBUFFERED=1

# ==============================================
# 3. CARPETA DE TRABAJO
# ==============================================

# Establece /app como carpeta principal de trabajo dentro del contenedor.
WORKDIR /app

# ==============================================
# 4. INSTALACIÓN DE DEPENDENCIAS
# ==============================================

# Copia el archivo requirements.txt al contenedor para instalar las dependencias del proyecto.
COPY requirements.txt /app/

# Actualiza pip e instala Django, Django REST Framework y las demás dependencias del proyecto.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================
# 5. COPIA DE LOS ARCHIVOS DEL PROYECTO
# ==============================================

# Copia todos los archivos y carpetas del proyecto Django hacia la carpeta /app del contenedor.
COPY . /app/

# Recopila los archivos CSS, JavaScript e imágenes para utilizarlos en producción.
RUN python manage.py collectstatic --noinput

# ==============================================
# 6. PUERTO DE LA APLICACIÓN
# ==============================================

# Indica el puerto que utilizará nuestra aplicación cuando se ejecute.
EXPOSE 8000


# ==============================================
# 7. INICIO DE LA APLICACIÓN DJANGO
# ==============================================

# Ejecuta las migraciones de sesiones para crear las tablas necesarias en la base de datos.
# El parámetro --noinput permite realizar el proceso sin solicitar confirmaciones.
# Si las migraciones ya están aplicadas, Django no las ejecutará nuevamente.

# Inicia Django mediante Gunicorn, un servidor de aplicaciones adecuado para producción.
# Utiliza el puerto proporcionado por Render o el puerto 8000 si no existe esa variable.
CMD ["sh", "-c", "python manage.py migrate sessions --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
