from django.urls import path
from . import views

# Importar las vistas de las API del sistema
from . import api_views



urlpatterns = [
    # API: CONSULTAR TODAS LAS LLANTAS REGISTRADAS
    # Permite obtener la información de las llantas en formato JSON
    path('api/llantas/', api_views.api_listar_llantas, name='api_listar_llantas'),

    # API: CONSULTAR UNA LLANTA POR SU NÚMERO
    # Permite obtener los datos de una llanta específica
    path('api/llantas/<str:numero_llanta>/',api_views.api_consultar_llanta,name='api_consultar_llanta'),

    # API: CONSULTAR EL HISTORIAL DE INSPECCIONES DE UNA LLANTA
    # Permite consultar todas las inspecciones de una llanta identificada por su número
    path('api/llantas/<str:numero_llanta>/historial/',api_views.api_consultar_historial,name='api_consultar_historial'),

    # Dirección para consultar la ficha y el historial de una llanta
    path("administracion/historial/", views.consultar_historial,name="consultar_historial"),
    path("", views.login, name="login"),
    path("inicio/", views.inicio, name="inicio"),

    # Dirección para cambiar la situación administrativa de una llanta
    path("administracion/cambiar-situacion/<str:numero_llanta>/<str:nueva_situacion>/",views.cambiar_situacion,name="cambiar_situacion"),

    # Dirección para registrar el retiro físico de una llanta
    path("administracion/registrar-retiro/<str:numero_llanta>/",views.registrar_retiro_fisico,name="registrar_retiro_fisico"),

    # Cerrar sesión
    path("logout/", views.logout, name="logout"),

    # Dirección del módulo de Administración
    path("administracion/", views.administracion, name="administracion"),

    # Dirección para registrar una llanta nueva
    path("administracion/registrar/", views.registrar_llanta, name="registrar_llanta"),

    # Abrir el formulario para realizar una inspección
    path("inspecciones/<str:numero_llanta>/",views.nueva_inspeccion,name="nueva_inspeccion"),


    # API: REGISTRAR UNA NUEVA INSPECCIÓN
    # Permite registrar mediciones, estado, destino y fotografías de una llanta específica
    path('api/llantas/<str:numero_llanta>/inspecciones/',api_views.api_registrar_inspeccion,name='api_registrar_inspeccion'),

    # Mostrar el formulario HTML para probar el registro de inspecciones mediante la API
    path("api/prueba-inspeccion/<str:numero_llanta>/",views.formulario_api_inspeccion,name="formulario_api_inspeccion"),
]