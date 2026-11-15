
from django.db import models


class Llanta(models.Model):
    numero_llanta = models.CharField(max_length=20, primary_key=True)
    marca = models.CharField(max_length=50)
    diseño = models.CharField(max_length=100)
    diseño_reencauche = models.CharField(max_length=100, null=True, blank=True)
    dimension = models.CharField(max_length=30)
    dot = models.CharField(max_length=20, null=True, blank=True)

    id_almacen_actual = models.ForeignKey(
        "Almacen",
        on_delete=models.DO_NOTHING,
        db_column="id_almacen_actual",
        related_name="llantas"
    )

    situacion_administrativa = models.CharField(max_length=20, default="Activa")
    fecha_retiro_fisico = models.DateTimeField(null=True, blank=True)
    empresa_retiro = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "llantas"
        managed = False

    def __str__(self):
        return self.numero_llanta


class Almacen(models.Model):
    id_almacen = models.AutoField(primary_key=True)
    nombre_almacen = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "almacenes"
        managed = False

    def __str__(self):
        return self.nombre_almacen


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "roles"
        managed = False

    def __str__(self):
        return self.nombre_rol


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    usuario = models.CharField(max_length=50, unique=True)
    contraseña = models.CharField(max_length=255)

    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.DO_NOTHING,
        db_column="id_rol"
    )

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "usuarios"
        managed = False

    def __str__(self):
        return self.usuario
    
    # Modelo que representa la tabla de inspecciones de MySQL
class Inspeccion(models.Model):

    # Identificador único de cada inspección
    id_inspeccion = models.AutoField(primary_key=True)

    # Número de la llanta que fue inspeccionada
    numero_llanta = models.ForeignKey(
        Llanta,
        on_delete=models.DO_NOTHING,
        db_column="numero_llanta"
    )

    # Usuario que realizó la inspección
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column="id_usuario"
    )

    # Fecha y hora en que se realizó la inspección
    fecha_hora_inspeccion = models.DateTimeField()

    # Mediciones de profundidad de la banda de rodamiento
    profundidad_externa = models.DecimalField(max_digits=3, decimal_places=1)
    profundidad_central = models.DecimalField(max_digits=3, decimal_places=1)
    profundidad_interna = models.DecimalField(max_digits=3, decimal_places=1)

    # Estado asignado a la llanta según el resultado de la inspección
    estado = models.CharField(max_length=20)

    # Observaciones adicionales; este campo puede estar vacío
    observaciones = models.TextField(null=True, blank=True)

    # Almacén al que se destina la llanta después de la inspección
    id_almacen_destino = models.ForeignKey(
        Almacen,
        on_delete=models.DO_NOTHING,
        db_column="id_almacen_destino"
    )

    class Meta:
        # Nombre exacto de la tabla existente en MySQL
        db_table = "inspecciones"

        # Indica que Django no debe crear, modificar ni eliminar esta tabla
        managed = False

    # Representación de la inspección cuando se consulta como objeto
    def __str__(self):
        return f"Inspección {self.id_inspeccion} - {self.numero_llanta_id}"
    
    # Modelo que representa la tabla de evidencias de MySQL
class Evidencia(models.Model):

    # Identificador único de cada evidencia
    id_evidencia = models.AutoField(primary_key=True)

    # Inspección a la que pertenece la evidencia
    id_inspeccion = models.ForeignKey(
        Inspeccion,
        on_delete=models.DO_NOTHING,
        db_column="id_inspeccion"
    )

    # Ruta donde se encuentra almacenada la fotografía
    ruta_archivo = models.CharField(max_length=255)

    # Fecha y hora en que se cargó la evidencia
    fecha_carga = models.DateTimeField()

    class Meta:
        db_table = "evidencias"
        managed = False

    def __str__(self):
        return f"Evidencia {self.id_evidencia}"
