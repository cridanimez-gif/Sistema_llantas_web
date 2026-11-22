from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password

# Herramientas para manejar la fecha y hora de las inspecciones
from django.utils import timezone

# Importar los modelos necesarios para gestionar las llantas
from .models import Llanta, Usuario, Almacen, Inspeccion, Evidencia, Rol

# Herramientas para validar y manejar valores decimales
from decimal import Decimal, InvalidOperation

# Permitir guardar la llanta y su inspección como una sola operación
from django.db import transaction, IntegrityError

# Importar el sistema de mensajes de Django
from django.contrib import messages

# Herramienta para guardar las fotografías de las inspecciones
from django.core.files.storage import default_storage

from django.shortcuts import render, redirect, get_object_or_404


# =====================================================
# INICIO DE SESIÓN
# =====================================================

def login(request):
    # Inicializar el mensaje de error
    error = ""

    # Procesar los datos cuando se envía el formulario
    if request.method == "POST":
        nombre_usuario = request.POST.get("usuario", "").strip()
        contrasena = request.POST.get("contrasena", "")

        try:
            # Buscar un usuario activo en la base de datos
            usuario = Usuario.objects.get(
                usuario=nombre_usuario,
                activo=True
            )

            # Verificar que la contraseña sea correcta
            if check_password(contrasena, usuario.contraseña):
                # Guardar los datos del usuario en la sesión
                request.session["id_usuario"] = usuario.id_usuario
                request.session["nombre_usuario"] = usuario.nombre
                request.session["id_rol"] = usuario.id_rol_id

                # Ingresar al módulo de Gestión de Llantas
                return redirect("inicio")

            else:
                # Mostrar un mensaje si la contraseña es incorrecta
                error = "El usuario o la contraseña son incorrectos."

        except Usuario.DoesNotExist:
            # Mostrar un mensaje si el usuario no existe
            error = "El usuario o la contraseña son incorrectos."

    # Mostrar la página de inicio de sesión
    return render(request, "llantas/login.html", {"error": error})


# =====================================================
# CERRAR SESIÓN
# =====================================================

def logout(request):
    # Cerrar la sesión y eliminar sus datos
    request.session.flush()

    # Regresar a la página de inicio de sesión
    return redirect("login")


# =====================================================
# MÓDULO DE REGISTRO DE USUARIOS
# =====================================================

def registrar_usuario(request):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Permitir el acceso únicamente al Ingeniero
    if request.session.get("id_rol") != 3:
        return redirect("inicio")

    # Inicializar los mensajes
    mensaje_error = ""
    mensaje_exito = ""

    # Procesar el formulario cuando se envía
    if request.method == "POST":

        # Obtener los datos ingresados
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        nombre_usuario = request.POST.get("usuario", "").strip()
        contrasena = request.POST.get("contrasena", "")
        confirmar_contrasena = request.POST.get(
            "confirmar_contrasena", ""
        )
        id_rol = request.POST.get("id_rol", "")

        try:
            # Verificar que todos los campos estén completos
            if not all([
                nombre, apellido, nombre_usuario,
                contrasena, confirmar_contrasena, id_rol
            ]):
                raise ValueError("Completa todos los campos.")

            # Validar la longitud de los datos
            if len(nombre) > 50 or len(apellido) > 50:
                raise ValueError("El nombre y apellido admiten máximo 50 caracteres.")

            if len(nombre_usuario) > 50:
                raise ValueError("El usuario admite máximo 50 caracteres.")

            # Verificar que las contraseñas coincidan
            if contrasena != confirmar_contrasena:
                raise ValueError("Las contraseñas no coinciden.")

            # Exigir una contraseña de al menos 8 caracteres
            if len(contrasena) < 8:
                raise ValueError("La contraseña debe tener al menos 8 caracteres.")

            # Consultar el rol seleccionado
            rol = Rol.objects.get(id_rol=id_rol)

            # Verificar que el nombre de usuario no exista
            if Usuario.objects.filter(usuario=nombre_usuario).exists():
                raise ValueError("Ese nombre de usuario ya está registrado.")

            # Guardar el nuevo usuario con contraseña protegida
            Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                usuario=nombre_usuario,
                contraseña=make_password(contrasena),
                id_rol=rol,
                activo=True
            )

            mensaje_exito = "El usuario fue registrado exitosamente."

        except Rol.DoesNotExist:
            mensaje_error = "El rol seleccionado no es válido."

        except ValueError as error:
            mensaje_error = str(error)

        except IntegrityError:
            mensaje_error = "No fue posible registrar el usuario. Verifica los datos."

    # Consultar los roles disponibles
    roles = Rol.objects.all().order_by("id_rol")

    # Preparar la información para la página
    contexto = {
        "nombre_usuario": request.session.get("nombre_usuario"),
        "roles": roles,
        "mensaje_error": mensaje_error,
        "mensaje_exito": mensaje_exito,
    }

    # Mostrar el formulario de registro de usuarios
    return render(
        request,
        "llantas/registrar_usuario.html",
        contexto
    )


# =====================================================
# MÓDULO DE CAMBIO DE CONTRASEÑA
# =====================================================

def cambiar_contrasena(request):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Consultar los datos del usuario que inició sesión
    try:
        usuario = Usuario.objects.get(
            id_usuario=request.session["id_usuario"],
            activo=True
        )
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect("login")

    # Inicializar los mensajes
    mensaje_error = ""
    mensaje_exito = ""

    # Procesar el formulario cuando se envía
    if request.method == "POST":

        # Obtener las contraseñas ingresadas
        contrasena_actual = request.POST.get("contrasena_actual", "")
        nueva_contrasena = request.POST.get("nueva_contrasena", "")
        confirmar_contrasena = request.POST.get(
            "confirmar_contrasena", ""
        )

        # Verificar que todos los campos estén completos
        if not all([
            contrasena_actual,
            nueva_contrasena,
            confirmar_contrasena
        ]):
            mensaje_error = "Completa todos los campos."

        # Comprobar la contraseña actual
        elif not check_password(contrasena_actual, usuario.contraseña):
            mensaje_error = "La contraseña actual es incorrecta."

        # Verificar la longitud de la nueva contraseña
        elif len(nueva_contrasena) < 8:
            mensaje_error = "La nueva contraseña debe tener al menos 8 caracteres."

        # Verificar que la nueva contraseña y su confirmación coincidan
        elif nueva_contrasena != confirmar_contrasena:
            mensaje_error = "Las nuevas contraseñas no coinciden."

        # Evitar que se vuelva a utilizar la misma contraseña
        elif check_password(nueva_contrasena, usuario.contraseña):
            mensaje_error = "La nueva contraseña debe ser diferente a la actual."

        else:
            # Proteger y guardar la nueva contraseña
            usuario.contraseña = make_password(nueva_contrasena)
            usuario.save(update_fields=["contraseña"])

            mensaje_exito = "Tu contraseña fue actualizada correctamente."

    # Preparar la información para mostrar la página
    contexto = {
        "nombre_usuario": usuario.nombre,
        "mensaje_error": mensaje_error,
        "mensaje_exito": mensaje_exito,
    }

    # Mostrar el formulario de cambio de contraseña
    return render(
        request,
        "llantas/cambiar_contrasena.html",
        contexto
    )




# =====================================================
# MÓDULO DE GESTIÓN DE LLANTAS
# =====================================================

def inicio(request):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Inicializar las variables de consulta
    numero_llanta = ""
    ubicacion_seleccionada = ""
    estado_seleccionado = ""
    llanta_consultada = None
    llantas_resultado = None
    mensaje_consulta = ""

    # Procesar las consultas enviadas mediante GET
    if request.method == "GET":
        numero_llanta = request.GET.get("numero_llanta", "").strip()
        ubicacion_seleccionada = request.GET.get("ubicacion", "")
        estado_seleccionado = request.GET.get("estado", "")

        # Consultar por número de llanta
        if numero_llanta:
            try:
                # Buscar la llanta por su número
                llanta_consultada = Llanta.objects.get(
                    numero_llanta=numero_llanta
                )

                # Consultar la última inspección de esa llanta
                ultima_inspeccion = Inspeccion.objects.filter(
                    numero_llanta_id=numero_llanta
                ).order_by(
                    "-fecha_hora_inspeccion", "-id_inspeccion"
                ).first()

                # Obtener el estado de su última inspección
                if ultima_inspeccion:
                    llanta_consultada.estado_inspeccion = ultima_inspeccion.estado

                elif llanta_consultada.id_almacen_actual.nombre_almacen in [
                    "Contenedor", "Jaula"
                ]:
                    llanta_consultada.estado_inspeccion = "Stock"

                else:
                    llanta_consultada.estado_inspeccion = "Sin inspección previa"

            except Llanta.DoesNotExist:
                # Informar cuando no se encuentra la llanta
                mensaje_consulta = "No se encontró una llanta con ese número."

        # Consultar llantas por ubicación
        elif ubicacion_seleccionada:
            llantas_resultado = Llanta.objects.filter(
                id_almacen_actual__nombre_almacen=ubicacion_seleccionada
            ).order_by("numero_llanta")

        # Consultar llantas por estado de inspección
        elif estado_seleccionado:
            llantas_resultado = []

            # Recorrer las llantas registradas
            for llanta in Llanta.objects.all().order_by("numero_llanta"):
                # Consultar la última inspección de cada llanta
                ultima_inspeccion = Inspeccion.objects.filter(
                    numero_llanta_id=llanta.numero_llanta
                ).order_by(
                    "-fecha_hora_inspeccion", "-id_inspeccion"
                ).first()

                # Determinar el estado actual de la llanta
                if ultima_inspeccion:
                    estado_actual = ultima_inspeccion.estado

                elif llanta.id_almacen_actual.nombre_almacen in [
                    "Contenedor", "Jaula"
                ]:
                    estado_actual = "Stock"

                else:
                    estado_actual = "Sin inspección previa"

                # Agregar la llanta si coincide con el estado buscado
                if estado_actual == estado_seleccionado:
                    llanta.estado_inspeccion = estado_actual
                    llantas_resultado.append(llanta)

    # Obtener todas las llantas para mostrar el inventario
    llantas = Llanta.objects.all().order_by("numero_llanta")

    # Obtener las ubicaciones disponibles
    almacenes = Almacen.objects.all().order_by("nombre_almacen")

    # Identificar el rol del usuario que inició sesión
    id_rol = request.session.get("id_rol")

    # Permitir la administración únicamente al Analista y al Ingeniero
    puede_administrar = id_rol in [2, 3]

    # Preparar la información que recibirá la página
    contexto = {
        "llantas": llantas,
        "llanta_consultada": llanta_consultada,
        "numero_consultado": numero_llanta,
        "mensaje_consulta": mensaje_consulta,
        "llantas_resultado": llantas_resultado,
        "almacenes": almacenes,
        "ubicacion_seleccionada": ubicacion_seleccionada,
        "estado_seleccionado": estado_seleccionado,
        "nombre_usuario": request.session.get("nombre_usuario"),
        "id_rol": id_rol,
        "puede_administrar": puede_administrar,
        "estados": ["Stock", "Reencauche", "Ajuste/RM", "Garantía", "Desecho"],
        "titulo": "Sistema de Gestión y Control de Inventario de Llantas",
        "mensaje": "Bienvenido al sistema de gestión de llantas del taller.",
        "version": "1.0"
    }

    # Mostrar el módulo de Gestión de Llantas
    return render(request, "llantas/inicio.html", contexto)


# =====================================================
# MÓDULO DE ADMINISTRACIÓN DE LLANTAS
# =====================================================

def administracion(request):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Obtener el rol del usuario conectado
    id_rol = request.session.get("id_rol")

    # Permitir el acceso únicamente al Analista y al Ingeniero
    if id_rol not in [2, 3]:
        return redirect("inicio")

    # Preparar la información inicial de la página
    contexto = {
        "nombre_usuario": request.session.get("nombre_usuario"),
        "id_rol": id_rol,
        "numero_busqueda": "",
        "llanta_consultada": None,
        "mensaje_consulta": "",
        "ultima_inspeccion": None,
    }

    # Procesar la búsqueda cuando se envía el formulario
    if request.method == "POST":

        # Obtener el número de llanta ingresado
        numero_llanta = request.POST.get("numero_llanta", "").strip()

        # Conservar el número escrito en el campo de búsqueda
        contexto["numero_busqueda"] = numero_llanta

        # Verificar que se haya ingresado un número
        if numero_llanta:

            try:
                # Buscar la llanta en la base de datos
                llanta = Llanta.objects.get(numero_llanta=numero_llanta)

                # Enviar la llanta encontrada a la página
                contexto["llanta_consultada"] = llanta

                # Consultar la última inspección de la llanta
                ultima_inspeccion = Inspeccion.objects.filter(
                    numero_llanta_id=numero_llanta
                ).order_by(
                    "-fecha_hora_inspeccion",
                    "-id_inspeccion"
                ).first()

                # Enviar la última inspección a la página
                contexto["ultima_inspeccion"] = ultima_inspeccion

            except Llanta.DoesNotExist:

                # Informar cuando no exista una llanta con ese número
                contexto["mensaje_consulta"] = (
                    "No se encontró una llanta con ese número."
                )

        else:

            # Informar cuando el campo esté vacío
            contexto["mensaje_consulta"] = (
                "Debes ingresar el número de la llanta."
            )

    # Mostrar la pantalla de Administración de Llantas
    return render(request, "llantas/administracion.html", contexto)


# =====================================================
# CONSULTAR HISTORIAL DE LLANTAS
# =====================================================

def consultar_historial(request):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Permitir el acceso únicamente al Analista y al Ingeniero
    if request.session.get("id_rol") not in [2, 3]:
        return redirect("inicio")

    # Preparar los datos iniciales de la página
    contexto = {
        "nombre_usuario": request.session.get("nombre_usuario"),
        "numero_busqueda": "",
        "llanta": None,
        "inspecciones": [],
        "mensaje": "",
    }

    # Procesar la búsqueda cuando se envía el formulario
    if request.method == "POST":

        # Obtener el número de llanta ingresado
        numero_llanta = request.POST.get("numero_llanta", "").strip()

        # Guardar el número para conservarlo en el formulario
        contexto["numero_busqueda"] = numero_llanta

        # Verificar que se haya escrito un número
        if numero_llanta:

            try:
                # Buscar la llanta en la base de datos
                llanta = Llanta.objects.get(numero_llanta=numero_llanta)

                # Consultar las inspecciones de esa llanta
                # Ordenar por fecha y, si coinciden, por número de inspección
                inspecciones = Inspeccion.objects.filter(
                numero_llanta_id=numero_llanta
                ).order_by("-fecha_hora_inspeccion", "-id_inspeccion")

                # Enviar la información encontrada a la página
                contexto["llanta"] = llanta
                contexto["inspecciones"] = inspecciones

            except Llanta.DoesNotExist:

                # Informar cuando la llanta no esté registrada
                contexto["mensaje"] = (
                    "No se encontró una llanta con ese número."
                )

        else:

            # Informar cuando el campo esté vacío
            contexto["mensaje"] = "Debes ingresar un número de llanta."

    # Mostrar la página con los resultados de la consulta
    return render(request, "llantas/consultar_historial.html", contexto)


# =====================================================
# CAMBIAR SITUACIÓN ADMINISTRATIVA DE UNA LLANTA
# =====================================================

def cambiar_situacion(request, numero_llanta, nueva_situacion):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Permitir el acceso únicamente al Analista y al Ingeniero
    if request.session.get("id_rol") not in [2, 3]:
        return redirect("inicio")

    # Permitir cambios únicamente mediante formularios POST
    if request.method != "POST":
        return redirect("administracion")

    # Aceptar únicamente las situaciones administrativas permitidas
    if nueva_situacion not in ["Congelada", "Activa", "Desactivada"]:
        messages.error(request, "La situación solicitada no es válida.")
        return redirect("administracion")

    # Consultar la llanta seleccionada
    try:
        llanta = Llanta.objects.get(numero_llanta=numero_llanta)

    except Llanta.DoesNotExist:
        messages.error(request, "No se encontró la llanta seleccionada.")
        return redirect("administracion")

    # Consultar la última inspección de la llanta
    ultima_inspeccion = Inspeccion.objects.filter(
        numero_llanta_id=numero_llanta
    ).order_by("-fecha_hora_inspeccion", "-id_inspeccion").first()

    # Obtener la situación administrativa actual
    actual = llanta.situacion_administrativa

    # Obtener la ubicación física actual
    ubicacion = llanta.id_almacen_actual.nombre_almacen

    # Obtener el último estado registrado en una inspección
    estado = ultima_inspeccion.estado if ultima_inspeccion else None

    # Evitar modificar llantas retiradas físicamente
    if actual == "Retirada":
        messages.error(request, "La llanta ya fue retirada físicamente.")
        return redirect("administracion")

    # Validar las condiciones para congelar
    if nueva_situacion == "Congelada" and actual != "Activa":
        messages.error(request, "Solo se pueden congelar llantas activas.")
        return redirect("administracion")

    # Validar las condiciones para reactivar
    if nueva_situacion == "Activa" and actual != "Congelada":
        messages.error(request, "Solo se pueden reactivar llantas congeladas.")
        return redirect("administracion")

    # Validar las condiciones para desactivar
    if nueva_situacion == "Desactivada":

        if ubicacion != "Pila de Desecho" or estado != "Desecho":
            messages.error(
                request,
                "Solo se pueden desactivar llantas ubicadas en Pila de Desecho "
                "y cuya última inspección indique Desecho."
            )
            return redirect("administracion")

        if actual not in ["Activa", "Congelada"]:
            messages.error(
                request,
                "La situación actual de la llanta no permite desactivarla."
            )
            return redirect("administracion")

    # Actualizar la situación administrativa
    llanta.situacion_administrativa = nueva_situacion
    llanta.save(update_fields=["situacion_administrativa"])

    # Informar que el cambio se realizó correctamente
    messages.success(
        request,
        f"La llanta {numero_llanta} ahora figura como {nueva_situacion}."
    )

    # Regresar al módulo de administración
    return redirect("administracion")


# =====================================================
# REGISTRAR RETIRO FÍSICO DE UNA LLANTA
# =====================================================

def registrar_retiro_fisico(request, numero_llanta):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Permitir el acceso únicamente al Analista y al Ingeniero
    if request.session.get("id_rol") not in [2, 3]:
        return redirect("inicio")

    # Permitir el registro únicamente mediante formularios POST
    if request.method != "POST":
        return redirect("administracion")

    # Consultar la llanta seleccionada
    try:
        llanta = Llanta.objects.get(numero_llanta=numero_llanta)

    except Llanta.DoesNotExist:
        messages.error(request, "No se encontró la llanta seleccionada.")
        return redirect("administracion")

    # Evitar registrar nuevamente una llanta retirada
    if llanta.situacion_administrativa == "Retirada":
        messages.error(request, "Esta llanta ya fue retirada físicamente.")
        return redirect("administracion")

    # Consultar la última inspección de la llanta
    ultima_inspeccion = Inspeccion.objects.filter(
        numero_llanta_id=numero_llanta
    ).order_by("-fecha_hora_inspeccion", "-id_inspeccion").first()

    # Obtener la ubicación física actual
    ubicacion = llanta.id_almacen_actual.nombre_almacen

    # Verificar que la llanta esté en Pila de Desecho
    if ubicacion != "Pila de Desecho" or not ultima_inspeccion or ultima_inspeccion.estado != "Desecho":
        messages.error(
            request,
            "Solo se pueden retirar llantas ubicadas en Pila de Desecho "
            "y cuya última inspección indique Desecho."
        )
        return redirect("administracion")

    # Obtener el nombre de la empresa encargada del retiro
    empresa = request.POST.get("empresa_retiro", "").strip()

    # Verificar que se haya ingresado el nombre de la empresa
    if not empresa:
        messages.error(request, "Debes ingresar el nombre de la empresa.")
        return redirect("administracion")
    # Verificar que el nombre no supere los 100 caracteres
    if len(empresa) > 100:
        messages.error(
            request,
            "El nombre de la empresa no puede superar los 100 caracteres."
        )
        return redirect("administracion")

    # Registrar la fecha, la empresa y la situación de retiro
    from django.utils import timezone

    llanta.situacion_administrativa = "Retirada"
    llanta.fecha_retiro_fisico = timezone.now()
    llanta.empresa_retiro = empresa

    # Guardar los cambios en la base de datos
    llanta.save(
        update_fields=[
            "situacion_administrativa",
            "fecha_retiro_fisico",
            "empresa_retiro",
        ]
    )

    # Informar que el retiro físico se registró correctamente
    messages.success(
        request,
        f"Se registró el retiro físico de la llanta {numero_llanta} "
        f"por parte de {empresa}."
    )

    # Regresar al módulo de administración
    return redirect("administracion")


# =====================================================
# REGISTRO DE LLANTAS NUEVAS
# =====================================================

def registrar_llanta(request):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Obtener el rol del usuario conectado
    id_rol = request.session.get("id_rol")

    # Permitir el registro únicamente al Analista y al Ingeniero
    if id_rol not in [2, 3]:
        return redirect("inicio")

    # Consultar únicamente las ubicaciones permitidas
    almacenes = Almacen.objects.filter(
        nombre_almacen__in=["Contenedor", "Jaula"]
    ).order_by("nombre_almacen")

    # Recuperar el mensaje de un registro exitoso
    mensaje_exito = request.session.pop("mensaje_registro", "")

    # Inicializar el mensaje de error
    mensaje_error = ""

    # Procesar el formulario cuando se envía
    if request.method == "POST":

        # Obtener los datos de identificación de la llanta
        numero = request.POST.get("numero_llanta", "").strip()
        marca = request.POST.get("marca", "").strip()
        diseno = request.POST.get("diseno", "").strip()
        diseno_reencauche = request.POST.get(
            "diseno_reencauche", ""
        ).strip()
        dimension = request.POST.get("dimension", "").strip()
        dot = request.POST.get("dot", "").strip()
        id_almacen = request.POST.get("almacen", "")

        try:
            # Verificar que los campos obligatorios estén completos
            if not numero or not marca or not diseno or not dimension:
                raise ValueError("Completa todos los campos obligatorios.")

            # Verificar que el número no supere 20 caracteres
            if len(numero) > 20:
                raise ValueError(
                    "El número de llanta no puede superar 20 caracteres."
                )

            # Convertir las tres mediciones a números decimales
            profundidad_externa = Decimal(
                request.POST.get("profundidad_externa", "")
            )
            profundidad_central = Decimal(
                request.POST.get("profundidad_central", "")
            )
            profundidad_interna = Decimal(
                request.POST.get("profundidad_interna", "")
            )

            # Agrupar las mediciones para facilitar su validación
            profundidades = [
                profundidad_externa,
                profundidad_central,
                profundidad_interna
            ]

            # Validar que las mediciones estén dentro del rango permitido
            for profundidad in profundidades:
                if (
                    profundidad < 0
                    or profundidad > Decimal("99.9")
                    or profundidad != profundidad.quantize(Decimal("0.1"))
                ):
                    raise ValueError(
                        "Las profundidades deben tener máximo un decimal "
                        "y estar entre 0 y 99.9."
                    )

            # Verificar que se haya seleccionado una ubicación inicial
            if not id_almacen:
                raise ValueError("Selecciona una ubicación inicial.")

            # Comprobar que la ubicación seleccionada esté permitida
            almacen = Almacen.objects.get(
                id_almacen=id_almacen,
                nombre_almacen__in=["Contenedor", "Jaula"]
            )

            # Obtener el usuario que realiza el registro
            usuario = Usuario.objects.get(
                id_usuario=request.session["id_usuario"]
            )

            # Verificar que la llanta no esté registrada previamente
            if Llanta.objects.filter(numero_llanta=numero).exists():
                raise ValueError(
                    "Ya existe una llanta registrada con ese número."
                )

            # Guardar la llanta y su inspección inicial
            # dentro de una sola transacción
            with transaction.atomic():

                # Registrar la información general de la llanta
                llanta = Llanta.objects.create(
                    numero_llanta=numero,
                    marca=marca,
                    diseño=diseno,
                    diseño_reencauche=diseno_reencauche or None,
                    dimension=dimension,
                    dot=dot or None,
                    id_almacen_actual=almacen,
                    situacion_administrativa="Activa"
                )

                # Crear la inspección inicial con las mediciones ingresadas
                Inspeccion.objects.create(
                    numero_llanta=llanta,
                    id_usuario=usuario,
                    fecha_hora_inspeccion=timezone.now(),
                    profundidad_externa=profundidad_externa,
                    profundidad_central=profundidad_central,
                    profundidad_interna=profundidad_interna,
                    estado="Stock",
                    observaciones="Registro inicial de llanta nueva.",
                    id_almacen_destino=almacen
                )

            # Preparar el mensaje de confirmación del registro
            request.session["mensaje_registro"] = (
                f"La llanta {numero} fue registrada exitosamente."
            )

            # Regresar al formulario para permitir otro registro
            return redirect("registrar_llanta")

        except (InvalidOperation, ValueError) as error:
            # Mostrar el mensaje cuando los datos no sean válidos
            mensaje_error = str(error)

        except Almacen.DoesNotExist:
            # Informar cuando la ubicación seleccionada no sea válida
            mensaje_error = "La ubicación seleccionada no es válida."

        except Usuario.DoesNotExist:
            # Informar cuando no se encuentre el usuario responsable
            mensaje_error = "No se encontró el usuario que realiza el registro."

        except IntegrityError:
            # Informar cuando la base de datos rechace el registro
            mensaje_error = (
                "No fue posible completar el registro. "
                "Verifica que la llanta no exista y vuelve a intentarlo."
            )

    # Preparar la información para mostrar la pantalla de registro
    contexto = {
        "nombre_usuario": request.session.get("nombre_usuario"),
        "almacenes": almacenes,
        "mensaje_error": mensaje_error,
        "mensaje_exito": mensaje_exito,
    }

    # Mostrar el formulario de registro de llantas
    return render(
        request,
        "llantas/registrar_llanta.html",
        contexto
    )


# ============================================================
# PREPARAR UNA NUEVA INSPECCIÓN
# ============================================================
# Registrar una nueva inspección realizada por el técnico
def nueva_inspeccion(request, numero_llanta):

    # Verificar que el usuario haya iniciado sesión
    if "id_usuario" not in request.session:
        return redirect("login")

    # Permitir realizar inspecciones a los tres roles del sistema
    if str(request.session.get("id_rol")) not in ["1", "2", "3"]:
        return redirect("inicio")

    # Buscar la llanta que se va a inspeccionar
    try:
        llanta = Llanta.objects.get(numero_llanta=numero_llanta)

    except Llanta.DoesNotExist:
        messages.error(request, "No se encontró la llanta indicada.")
        return redirect("inicio")

    # Consultar la inspección más reciente de la llanta
    ultima_inspeccion = Inspeccion.objects.filter(
        numero_llanta_id=numero_llanta
    ).order_by(
        "-fecha_hora_inspeccion",
        "-id_inspeccion"
    ).first()

    # Consultar los almacenes permitidos como destino de la inspección
    almacenes_destino = Almacen.objects.filter(
        nombre_almacen__in=[
            "Rack de Stock",
            "Pila para Reencauche",
            "Pila Ajuste/RM",
            "Pila de Desecho",
            "Rack Garantías"
        ]
    ).order_by("id_almacen")

    # Procesar el formulario cuando el técnico lo envíe
    if request.method == "POST":

        # Obtener las profundidades registradas por el técnico
        try:
            profundidad_externa = Decimal(
                request.POST.get("profundidad_externa", "")
            )
            profundidad_central = Decimal(
                request.POST.get("profundidad_central", "")
            )
            profundidad_interna = Decimal(
                request.POST.get("profundidad_interna", "")
            )

            # Agrupar las profundidades para validarlas
            profundidades = [
                profundidad_externa,
                profundidad_central,
                profundidad_interna
            ]

            # Validar que sean valores numéricos dentro del rango permitido
            if any(
                not valor.is_finite()
                or valor < 0
                or valor > Decimal("99.9")
                or valor != valor.quantize(Decimal("0.1"))
                for valor in profundidades
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(
                request,
                "Las profundidades deben ser valores numéricos válidos "
                "con máximo un decimal."
            )

        else:

            # Obtener el almacén seleccionado por el técnico
            id_almacen = request.POST.get("id_almacen")

            # Obtener las fotografías adjuntas
            fotografias = request.FILES.getlist("fotografias")

            # Validar la cantidad máxima de fotografías
            if len(fotografias) > 5:
                messages.error(
                    request,
                    "Solo se permite adjuntar un máximo de cinco fotografías."
                )

            else:

                # Verificar que el almacén seleccionado sea válido
                almacen = Almacen.objects.filter(
                    id_almacen=id_almacen,
                    nombre_almacen__in=[
                        "Rack de Stock",
                        "Pila para Reencauche",
                        "Pila Ajuste/RM",
                        "Pila de Desecho",
                        "Rack Garantías"
                    ]
                ).first()

                if not almacen:
                    messages.error(
                        request,
                        "Seleccione un almacén de destino válido."
                    )

                # Para Desecho se requieren entre cuatro y cinco fotografías
                elif (
                    almacen.nombre_almacen == "Pila de Desecho"
                    and not 4 <= len(fotografias) <= 5
                ):
                    messages.error(
                        request,
                        "Para enviar una llanta a desecho debe adjuntar "
                        "entre cuatro y cinco fotografías."
                    )

                # Validar las extensiones de las fotografías
                elif any(
                    not foto.name.lower().endswith(
                        (".jpg", ".jpeg", ".png")
                    )
                    for foto in fotografias
                ):
                    messages.error(
                        request,
                        "Las fotografías deben estar en formato JPG, JPEG o PNG."
                    )

                else:

                    # Relacionar cada almacén con el estado correspondiente
                    estados_por_almacen = {
                        "Rack de Stock": "Stock",
                        "Pila para Reencauche": "Reencauche",
                        "Pila Ajuste/RM": "Ajuste",
                        "Pila de Desecho": "Desecho",
                        "Rack Garantías": "Garantía"
                    }

                    # El estado se determina según el destino elegido
                    estado = estados_por_almacen[almacen.nombre_almacen]

                    # Obtener las observaciones escritas por el técnico
                    observaciones = request.POST.get(
                        "observaciones", ""
                    ).strip()

                    # Lista para controlar las fotografías guardadas
                    rutas_guardadas = []

                    try:

                        # Obtener el usuario que realiza la inspección
                        usuario = Usuario.objects.get(
                            id_usuario=request.session["id_usuario"]
                        )

                        # Guardar la inspección y actualizar la llanta
                        # como una sola operación en la base de datos
                        with transaction.atomic():

                            # Registrar la inspección
                            inspeccion = Inspeccion.objects.create(
                                numero_llanta=llanta,
                                id_usuario=usuario,
                                fecha_hora_inspeccion=timezone.now(),
                                profundidad_externa=profundidad_externa,
                                profundidad_central=profundidad_central,
                                profundidad_interna=profundidad_interna,
                                estado=estado,
                                observaciones=observaciones or None,
                                id_almacen_destino=almacen
                            )

                            # Actualizar la ubicación actual de la llanta
                            llanta.id_almacen_actual = almacen
                            llanta.save(
                                update_fields=["id_almacen_actual"]
                            )

                            # Guardar cada fotografía y registrar su ruta
                            for fotografia in fotografias:

                                ruta_archivo = default_storage.save(
                                    (
                                        f"evidencias/llantas/"
                                        f"{numero_llanta}/"
                                        f"{fotografia.name}"
                                    ),
                                    fotografia
                                )

                                # Registrar la ruta para poder eliminarla
                                # si ocurre un error en la operación
                                rutas_guardadas.append(ruta_archivo)

                                # Registrar la evidencia en MySQL
                                Evidencia.objects.create(
                                    id_inspeccion=inspeccion,
                                    ruta_archivo=ruta_archivo,
                                    fecha_carga=timezone.now()
                                )

                        # Informar que la inspección fue registrada
                        messages.success(
                            request,
                            "inspección registrada exitosamente."
                        )

                        # Regresar al formulario de la misma llanta
                        return redirect("nueva_inspeccion", numero_llanta=numero_llanta)

                    except (Usuario.DoesNotExist, IntegrityError, OSError):

                        # Eliminar las fotografías guardadas si ocurre un error
                        for ruta in rutas_guardadas:
                            if default_storage.exists(ruta):
                                default_storage.delete(ruta)

                        messages.error(
                            request,
                            "No fue posible guardar la inspección. "
                            "Verifique los datos e inténtelo nuevamente."
                        )

    # Preparar la información que se mostrará en el formulario
    contexto = {
        "nombre_usuario": request.session.get("nombre_usuario"),
        "llanta": llanta,
        "ultima_inspeccion": ultima_inspeccion,
        "almacenes_destino": almacenes_destino,
    }

    # Mostrar el formulario de inspección
    return render(
        request,
        "llantas/inspeccion.html",
        contexto
    )

    # ============================================================
# VISTA PARA MOSTRAR EL FORMULARIO DE PRUEBA DE LA API
# ============================================================

def formulario_api_inspeccion(request, numero_llanta):

    # Verificar que el usuario haya iniciado sesión
    if not request.session.get("id_usuario"):
        return redirect("login")

    # Buscar la llanta que se va a inspeccionar
    llanta = get_object_or_404(
        Llanta,
        numero_llanta=numero_llanta
    )

    # Consultar los almacenes disponibles
    almacenes = Almacen.objects.all().order_by("id_almacen")

    # Mostrar el formulario y enviarle los datos necesarios
    return render(
        request,
        "llantas/formulario_api_inspeccion.html",
        {
            "numero_llanta": llanta.numero_llanta,
            "almacenes": almacenes
        }
    )

