from django.urls import path
from . import views

urlpatterns = [
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
]