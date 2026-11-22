
"""
Configuración principal del proyecto Sistema de Gestión de Llantas.
"""

from pathlib import Path


# ==========================================================
# RUTAS PRINCIPALES DEL PROYECTO
# ==========================================================

# Directorio principal donde se encuentra el proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# SEGURIDAD Y MODO DE DESARROLLO
# ==========================================================

# Clave secreta utilizada internamente por Django.
# Importar las claves privadas del proyecto
from .secretos import SECRET_KEY, MYSQL_PASSWORD

# Activar el modo de desarrollo.
DEBUG = True

# Direcciones autorizadas para acceder al proyecto.
ALLOWED_HOSTS = []


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
# CONEXIÓN A LA BASE DE DATOS MYSQL
# ==========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gestion_llantas',
        'USER': 'root',
        'PASSWORD': MYSQL_PASSWORD,
        'HOST': 'localhost',
        'PORT': '3307',
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

# Dirección para cargar CSS, JavaScript e imágenes estáticas.
STATIC_URL = 'static/'


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
