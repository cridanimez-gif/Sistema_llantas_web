# ==============================================
# CONFIGURACIÓN WSGI DEL PROYECTO
# ==============================================

# WSGI permite la comunicación entre el servidor de aplicaciones (Gunicorn) y nuestro proyecto desarrollado con Django.

# Importa el módulo os para gestionar variables de entorno del sistema.
import os

# Importa la función que crea la aplicación WSGI de Django.
from django.core.wsgi import get_wsgi_application

# Indica cuál es el archivo de configuración principal de nuestro proyecto Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crea la aplicación WSGI que utilizará Gunicorn para comunicarse con Django.
application = get_wsgi_application()