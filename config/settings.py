
"""
Configuración principal del proyecto Sistema de Gestión de Llantas.
"""

from pathlib import Path



# ==========================================================
# IMPORTACIÓN DE HERRAMIENTAS
# ==========================================================

# Permite trabajar con las rutas y variables de entorno del sistema.
import os

# Permite informar errores cuando falta una configuración obligatoria.
from django.core.exceptions import ImproperlyConfigured

# Permite identificar la carpeta principal del proyecto.
from pathlib import Path

# Permite interpretar la dirección de conexión y obtener los parámetros de PostgreSQL.
from urllib.parse import urlparse, parse_qsl, unquote


# ==========================================================
# RUTAS PRINCIPALES DEL PROYECTO
# ==========================================================

# Directorio principal donde se encuentra el proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# SEGURIDAD Y MODO DE EJECUCIÓN
# ==========================================================

# Carga las claves privadas cuando el proyecto se ejecuta localmente.
try:
    from .secretos import SECRET_KEY as CLAVE_LOCAL
    from .secretos import MYSQL_PASSWORD as CONTRASENA_LOCAL
except ImportError:
    CLAVE_LOCAL = ''
    CONTRASENA_LOCAL = ''

# Obtiene la clave secreta desde el entorno o utiliza la configuración local.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', CLAVE_LOCAL)

# Impide iniciar Django si no se ha configurado una clave secreta.
if not SECRET_KEY:
    raise ImproperlyConfigured('No se ha configurado DJANGO_SECRET_KEY.')

# Activa el modo de desarrollo únicamente cuando la variable lo indica.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Define los servidores autorizados para acceder a la aplicación.
ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1,localhost'
).split(',')



# ==========================================================
# APLICACIONES INSTALADAS
# ==========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'llantas',
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==========================================================
# CONFIGURACIÓN DE DIRECCIONES Y PLANTILLAS
# ==========================================================

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



# ==========================================================
# 5. CONEXIÓN A LA BASE DE DATOS MYSQL
# ==========================================================

# Obtiene la contraseña de MySQL desde el entorno o utiliza la local.
CONTRASENA_MYSQL = os.environ.get(
    'MYSQL_PASSWORD',
    CONTRASENA_LOCAL
)


# Obtiene la dirección de conexión de PostgreSQL desde las variables del entorno.
DATABASE_URL = os.environ.get('DATABASE_URL')

# Si existe DATABASE_URL, Django utilizará PostgreSQL de Neon.
if DATABASE_URL:

    # Analiza los datos de conexión recibidos desde Neon.
    datos_postgres = urlparse(DATABASE_URL)

    DATABASES = {
        'default': {
            # Utiliza PostgreSQL como motor de base de datos.
            'ENGINE': 'django.db.backends.postgresql',

            # Nombre de la base de datos.
            'NAME': unquote(datos_postgres.path.lstrip('/')),

            # Usuario de PostgreSQL.
            'USER': unquote(datos_postgres.username or ''),

            # Contraseña obtenida de la variable de entorno.
            'PASSWORD': unquote(datos_postgres.password or ''),

            # Servidor de PostgreSQL.
            'HOST': datos_postgres.hostname,

            # Puerto de PostgreSQL.
            'PORT': datos_postgres.port or 5432,

            # Opciones de conexión, incluido el requisito SSL de Neon.
            'OPTIONS': dict(parse_qsl(datos_postgres.query)),
        }
    }

# Si no existe DATABASE_URL, Django seguirá utilizando MySQL local.
else:

    DATABASES = {
        'default': {
            # Motor de base de datos MySQL.
            'ENGINE': 'django.db.backends.mysql',

            # Nombre de la base de datos local.
            'NAME': os.environ.get('MYSQL_DATABASE', 'gestion_llantas'),

            # Usuario de MySQL.
            'USER': os.environ.get('MYSQL_USER', 'root'),

            # Contraseña de MySQL.
            'PASSWORD': CONTRASENA_MYSQL,

            # Servidor MySQL local.
            'HOST': os.environ.get('MYSQL_HOST', 'localhost'),

            # Puerto de MySQL.
            'PORT': os.environ.get('MYSQL_PORT', '3307'),
        }
    }



# ==========================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==========================================================
# IDIOMA Y ZONA HORARIA
# ==========================================================

# Idioma principal del sistema: español de Colombia.
LANGUAGE_CODE = 'es-co'

# Zona horaria correspondiente a Colombia.
TIME_ZONE = 'America/Bogota'

# Activar la internacionalización.
USE_I18N = True

# Permitir el manejo de fechas y horas con zona horaria.
USE_TZ = True


# ==========================================================
# ARCHIVOS ESTÁTICOS
# ==========================================================

# Dirección utilizada para acceder a los archivos estáticos.
STATIC_URL = '/static/'

# Carpeta donde Django reunirá los archivos estáticos para producción.
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ==========================================================
# ARCHIVOS MULTIMEDIA
# ==========================================================

# Dirección utilizada para acceder a las fotografías y archivos
# que los usuarios carguen desde el sistema.
MEDIA_URL = '/media/'

# Carpeta física donde Django almacenará esos archivos.
MEDIA_ROOT = BASE_DIR / 'media'


# ==========================================================
# CONFIGURACIÓN DEL CORREO ELECTRÓNICO
# ==========================================================

# Durante el desarrollo, los correos se muestran en la terminal.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
