
# ============================================================
# IMPORTACIONES
# ============================================================

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status

# Importar los modelos necesarios para consultar y registrar información
from .models import Llanta, Inspeccion, Usuario, Evidencia

# Importar los serializadores de llantas, historial e inspecciones
from .serializers import (
    LlantaSerializer,
    InspeccionHistorialSerializer,
    InspeccionRegistroSerializer
)

# Herramienta para buscar una llanta y devolver error 404 si no existe
from django.shortcuts import get_object_or_404

# Importar herramientas para manejar fechas y transacciones seguras
from django.utils import timezone
from django.db import transaction, IntegrityError

# Importar herramientas para almacenar las fotografías
from django.core.files.storage import default_storage

# Importar herramientas para recibir datos y fotografías
from rest_framework.parsers import MultiPartParser, FormParser

# Importar herramientas para validar los valores numéricos
from decimal import Decimal


# ============================================================
# API PARA CONSULTAR TODAS LAS LLANTAS
# ============================================================

@api_view(["GET"])
def api_listar_llantas(request):
    
    # Verificar que el usuario haya iniciado sesión
    if not request.session.get("id_usuario"):
        return Response(
            {"error": "Debe iniciar sesión para consultar las llantas."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Consultar todas las llantas registradas en la base de datos
    llantas = Llanta.objects.select_related(
        "id_almacen_actual"
    ).all().order_by("numero_llanta")

    # Convertir los registros al formato JSON
    serializer = LlantaSerializer(llantas, many=True)

    # Devolver la información al usuario que consume la API
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ============================================================
# API PARA CONSULTAR UNA LLANTA POR SU NÚMERO
# ============================================================

@api_view(["GET"])
def api_consultar_llanta(request, numero_llanta):
    
    # Verificar que el usuario haya iniciado sesión
    if not request.session.get("id_usuario"):
        return Response(
            {"error": "Debe iniciar sesión para consultar esta llanta."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Buscar la llanta por su número
    llanta = get_object_or_404(
        Llanta,
        numero_llanta=numero_llanta
    )

    # Convertir la información de la llanta al formato JSON
    serializer = LlantaSerializer(llanta)

    # Devolver la información con una respuesta HTTP 200
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ============================================================
# API PARA CONSULTAR EL HISTORIAL DE INSPECCIONES
# Devuelve las inspecciones de la más reciente a la más antigua
# ============================================================

@api_view(["GET"])
def api_consultar_historial(request, numero_llanta):
    
    # Verificar que el usuario haya iniciado sesión
    if not request.session.get("id_usuario"):
        return Response(
            {"error": "Debe iniciar sesión para consultar el historial."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Buscar la llanta por su número
    llanta = get_object_or_404(
        Llanta,
        numero_llanta=numero_llanta
    )

    # Consultar las inspecciones asociadas a esa llanta
    inspecciones = Inspeccion.objects.filter(
        numero_llanta_id=llanta.numero_llanta
    ).select_related(
        "id_usuario",
        "id_almacen_destino"
    ).order_by(
        "-fecha_hora_inspeccion",
        "-id_inspeccion"
    )

    # Convertir las inspecciones al formato JSON
    serializer = InspeccionHistorialSerializer(
        inspecciones,
        many=True
    )

    # Devolver el historial con una respuesta HTTP 200
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ============================================================
# API PARA REGISTRAR UNA NUEVA INSPECCIÓN
# Permite registrar mediciones, estado, destino y fotografías
# ============================================================

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def api_registrar_inspeccion(request, numero_llanta):

    # --------------------------------------------------------
    # 1. VERIFICAR LA SESIÓN DEL USUARIO
    # --------------------------------------------------------

    # Comprobar que el usuario haya iniciado sesión
    if not request.session.get("id_usuario"):
        return Response(
            {
                "error": "Debe iniciar sesión para registrar una inspección."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Consultar el usuario que inició sesión
    try:
        usuario = Usuario.objects.get(
            id_usuario=request.session["id_usuario"]
        )

    except Usuario.DoesNotExist:
        return Response(
            {"error": "El usuario no existe."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Verificar que el usuario esté activo
    if not usuario.activo:
        return Response(
            {"error": "El usuario se encuentra inactivo."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Verificar que el usuario tenga un rol autorizado
    if str(usuario.id_rol_id) not in ["1", "2", "3"]:
        return Response(
            {
                "error": "No tiene permisos para registrar inspecciones."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------------
    # 2. BUSCAR LA LLANTA QUE SERÁ INSPECCIONADA
    # --------------------------------------------------------

    try:
        llanta = Llanta.objects.get(
            numero_llanta=numero_llanta
        )

    except Llanta.DoesNotExist:
        return Response(
            {"error": "No se encontró la llanta indicada."},
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # 3. VALIDAR LOS DATOS RECIBIDOS
    # --------------------------------------------------------

    # Copiar los datos recibidos para validar los campos normales.
    # Las fotografías se procesan por separado porque se reciben
    # como varios archivos con el mismo nombre de campo.
    datos_recibidos = request.data.copy()

    datos_recibidos.pop("fotografias", None)

    # Crear el serializador con las mediciones, el almacén
    # y las observaciones recibidas.
    serializer = InspeccionRegistroSerializer(
        data=datos_recibidos
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Obtener los datos que ya fueron validados
    datos_validados = serializer.validated_data

    # Recuperar las profundidades validadas
    profundidades = {
        "profundidad_externa": datos_validados["profundidad_externa"],
        "profundidad_central": datos_validados["profundidad_central"],
        "profundidad_interna": datos_validados["profundidad_interna"]
    }

    # Comprobar que cada profundidad sea finita y esté dentro del rango
    for campo, profundidad in profundidades.items():

        if (
            not profundidad.is_finite()
            or profundidad < Decimal("0")
            or profundidad > Decimal("99.9")
        ):
            return Response(
                {
                    "error": (
                        f"El valor de {campo} debe estar "
                        "entre 0 y 99.9."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que tenga máximo un decimal
        if profundidad != profundidad.quantize(Decimal("0.1")):
            return Response(
                {
                    "error": (
                        f"El valor de {campo} debe tener "
                        "máximo un decimal."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # Obtener el almacén que el serializador ya validó
    almacen = datos_validados["id_almacen_destino"]

    # --------------------------------------------------------
    # 4. DETERMINAR EL ESTADO SEGÚN EL ALMACÉN DE DESTINO
    # --------------------------------------------------------

    # Definir los estados permitidos según el almacén seleccionado
    estados_por_almacen = {
        "Rack de Stock": "Stock",
        "Pila para Reencauche": "Reencauche",
        "Pila Ajuste/RM": "Ajuste",
        "Pila de Desecho": "Desecho",
        "Rack Garantías": "Garantía"
    }

    # Determinar el estado según el almacén de destino
    estado = estados_por_almacen.get(
        almacen.nombre_almacen
    )

    if not estado:
        return Response(
            {
                "error": (
                    "El almacén seleccionado no está "
                    "permitido como destino."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # 5. RECUPERAR LAS FOTOGRAFÍAS
    # --------------------------------------------------------

    # Obtener todas las fotografías enviadas desde el mismo campo.
    fotografias = request.FILES.getlist("fotografias")

    # Verificar que no se envíen más de cinco fotografías
    if len(fotografias) > 5:
        return Response(
            {
                "error": "Solo se permiten máximo cinco fotografías."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Para las llantas destinadas a Desecho se requieren
    # entre cuatro y cinco fotografías.
    if (
        almacen.nombre_almacen == "Pila de Desecho"
        and not 4 <= len(fotografias) <= 5
    ):
        return Response(
            {
                "error": (
                    "Para enviar una llanta a Desecho debe adjuntar "
                    "entre cuatro y cinco fotografías."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # 6. VALIDAR LOS FORMATOS DE LAS FOTOGRAFÍAS
    # --------------------------------------------------------

    # Extensiones de imagen permitidas
    extensiones_permitidas = [".jpg", ".jpeg", ".png"]

    for fotografia in fotografias:

        # Obtener la extensión del archivo
        extension = fotografia.name.lower().rsplit(".", 1)

        # Comprobar que la extensión sea válida
        if (
            len(extension) != 2
            or f".{extension[-1]}" not in extensiones_permitidas
        ):
            return Response(
                {
                    "error": (
                        "Las fotografías deben estar en formato "
                        "JPG, JPEG o PNG."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # --------------------------------------------------------
    # 7. OBTENER LAS OBSERVACIONES
    # --------------------------------------------------------

    observaciones = datos_validados.get(
        "observaciones",
        ""
    )

    # Lista para identificar los archivos guardados
    # y eliminarlos si ocurre un error
    rutas_guardadas = []

    # --------------------------------------------------------
    # 8. REGISTRAR LA INSPECCIÓN Y GUARDAR LAS EVIDENCIAS
    # --------------------------------------------------------

    try:

        # Realizar el registro dentro de una transacción segura
        with transaction.atomic():

            # Crear el registro de inspección
            inspeccion = Inspeccion.objects.create(
                numero_llanta=llanta,
                id_usuario=usuario,
                fecha_hora_inspeccion=timezone.now(),
                profundidad_externa=profundidades["profundidad_externa"],
                profundidad_central=profundidades["profundidad_central"],
                profundidad_interna=profundidades["profundidad_interna"],
                estado=estado,
                observaciones=observaciones,
                id_almacen_destino=almacen
            )

            # Actualizar el almacén actual de la llanta
            llanta.id_almacen_actual = almacen

            llanta.save(
                update_fields=["id_almacen_actual"]
            )

            # Guardar cada fotografía y relacionarla con la inspección
            for fotografia in fotografias:

                ruta = default_storage.save(
                    f"evidencias/llantas/{numero_llanta}/{fotografia.name}",
                    fotografia
                )

                # Registrar la ruta del archivo para controlar posibles errores
                rutas_guardadas.append(ruta)

                # Crear el registro de evidencia fotográfica
                Evidencia.objects.create(
                    id_inspeccion=inspeccion,
                    ruta_archivo=ruta,
                    fecha_carga=timezone.now()
                )

        # ----------------------------------------------------
        # 9. DEVOLVER LA RESPUESTA DEL REGISTRO
        # ----------------------------------------------------

        return Response(
            {
                "mensaje": "Inspección registrada correctamente.",
                "id_inspeccion": inspeccion.id_inspeccion,
                "numero_llanta": llanta.numero_llanta,
                "estado": estado,
                "almacen_destino": almacen.nombre_almacen,
                "fotografias_registradas": len(rutas_guardadas)
            },
            status=status.HTTP_201_CREATED
        )

    except (IntegrityError, OSError) as error:

        # Eliminar las fotografías guardadas si ocurre un error
        for ruta in rutas_guardadas:

            if default_storage.exists(ruta):
                default_storage.delete(ruta)

        return Response(
            {
                "error": "No fue posible registrar la inspección.",
                "detalle": str(error)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================
# CONFIGURAR EL SERIALIZADOR PARA EL FORMULARIO DE LA API
# Permite mostrar los campos del registro en el navegador
# ============================================================

def obtener_serializador_registro(self, *args, **kwargs):

    # Crear el serializador que mostrará los campos del formulario
    return InspeccionRegistroSerializer(
        *args,
        **kwargs
    )


# Asignar el serializador a la vista de registro
api_registrar_inspeccion.cls.get_serializer = obtener_serializador_registro
