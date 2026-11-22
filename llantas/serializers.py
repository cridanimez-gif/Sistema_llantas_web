
from rest_framework import serializers

# Importar los modelos que utiliza la API
from .models import Llanta, Inspeccion, Almacen


# ============================================================
# SERIALIZADOR DE LLANTAS
# ============================================================

class LlantaSerializer(serializers.ModelSerializer):

    # Convertir los datos del modelo Llanta a formato JSON
    class Meta:
        model = Llanta

        # Datos de la llanta que se pueden consultar mediante la API
        fields = [
            "numero_llanta",
            "marca",
            "diseño",
            "diseño_reencauche",
            "dimension",
            "dot",
            "id_almacen_actual",
            "situacion_administrativa",
            "fecha_retiro_fisico",
            "empresa_retiro",
        ]


# ============================================================
# SERIALIZADOR DEL HISTORIAL DE INSPECCIONES
# ============================================================

class InspeccionHistorialSerializer(serializers.ModelSerializer):

    # Mostrar el número de la llanta en lugar del objeto relacionado
    numero_llanta = serializers.CharField(
        source="numero_llanta.numero_llanta",
        read_only=True
    )

    # Obtener el nombre del técnico que realizó la inspección
    tecnico = serializers.SerializerMethodField()

    # Mostrar el nombre del almacén de destino
    almacen_destino = serializers.CharField(
        source="id_almacen_destino.nombre_almacen",
        read_only=True
    )

    class Meta:
        model = Inspeccion

        # Información que se mostrará en el historial
        fields = [
            "id_inspeccion",
            "numero_llanta",
            "fecha_hora_inspeccion",
            "tecnico",
            "profundidad_externa",
            "profundidad_central",
            "profundidad_interna",
            "estado",
            "observaciones",
            "almacen_destino",
        ]

    # Obtener el nombre completo del técnico
    def get_tecnico(self, obj):

        usuario = obj.id_usuario

        nombre = usuario.nombre or ""
        apellido = usuario.apellido or ""

        return f"{nombre} {apellido}".strip()


# ============================================================
# SERIALIZADOR PARA REGISTRAR UNA INSPECCIÓN
# ============================================================

class InspeccionRegistroSerializer(serializers.Serializer):

    # --------------------------------------------------------
    # MEDICIONES DE PROFUNDIDAD
    # --------------------------------------------------------

    # Profundidad medida en la parte externa de la llanta
    profundidad_externa = serializers.DecimalField(
        max_digits=4,
        decimal_places=1
    )

    # Profundidad medida en la parte central de la llanta
    profundidad_central = serializers.DecimalField(
        max_digits=4,
        decimal_places=1
    )

    # Profundidad medida en la parte interna de la llanta
    profundidad_interna = serializers.DecimalField(
        max_digits=4,
        decimal_places=1
    )

    # --------------------------------------------------------
    # ALMACÉN DE DESTINO
    # --------------------------------------------------------

    # Almacén al que se trasladará la llanta
    id_almacen = serializers.PrimaryKeyRelatedField(
        queryset=Almacen.objects.all(),
        source="id_almacen_destino"
    )

    # --------------------------------------------------------
    # OBSERVACIONES
    # --------------------------------------------------------

    # Observaciones registradas por el técnico
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )

