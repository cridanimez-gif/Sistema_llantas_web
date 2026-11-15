
"""
Configuración de las direcciones principales del proyecto
Sistema de Gestión y Control de Inventario de Llantas.
"""

# Importar las herramientas necesarias para administrar las direcciones
from django.contrib import admin
from django.urls import path, include

# Importar las herramientas para mostrar archivos multimedia
from django.conf import settings
from django.conf.urls.static import static


# ==========================================================
# DIRECCIONES PRINCIPALES DEL PROYECTO
# ==========================================================

urlpatterns = [

    # Dirección para acceder al panel administrativo de Django
    path('admin/', admin.site.urls),

    # Conectar las direcciones de la aplicación de gestión de llantas
    path('', include('llantas.urls')),
]


# ==========================================================
# CONFIGURACIÓN DE ARCHIVOS MULTIMEDIA
# ==========================================================

# Permitir mostrar fotografías y archivos multimedia durante
# el desarrollo del sistema.
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
