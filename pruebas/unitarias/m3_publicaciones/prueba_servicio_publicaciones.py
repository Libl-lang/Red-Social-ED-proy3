"""
Pruebas unitarias de ServicioPublicaciones.

Comprueban las reglas del módulo: publicar con sus validaciones y armar el
muro del usuario activo. Usan las piezas falsas de la Fase 0 (sesión,
directorio de usuarios, consulta de amistades y repositorio en memoria), así
que no necesitan archivos ni ventanas ni los módulos de otros integrantes.

Tabla de ejemplo: las publicaciones 1 (autor 2), 2 (autor 3), 3 (autor 2) y
4 (autor 1). Ana (id 1) es amiga de Beto (id 2) y no de Carla (id 3).
Las fechas están en 2020 para que una publicación nueva, que usa la fecha de
hoy, siempre sea más reciente sin depender del reloj del computador.
"""

from datetime import datetime, timezone

import pytest

from pruebas.falsos.consulta_amistades_falsa import ConsultaAmistadesFalsa
from pruebas.falsos.directorio_usuarios_falso import (
    USUARIOS_FALSOS,
    DirectorioUsuariosFalso,
)
from pruebas.falsos.repositorios_en_memoria import RepositorioPublicacionesEnMemoria
from pruebas.falsos.sesion_falsa import SesionFalsa
from social_una.dominio.errores import (
    ErrorAlmacenamiento,
    ErrorAutenticacion,
    ErrorValidacion,
)
from social_una.dominio.modelos import Publicacion
from social_una.servicios.servicio_publicaciones import (
    LARGO_MAXIMO_PUBLICACION,
    ServicioPublicaciones,
)


class RepositorioQueFalla(RepositorioPublicacionesEnMemoria):
    """Repositorio de prueba que siempre falla al guardar, para simular un disco con problemas."""

    def guardar_todo(self, publicaciones):
        raise ErrorAlmacenamiento("No se pudo guardar el archivo.")


def crear_publicaciones_de_ejemplo() -> list[Publicacion]:
    """Devuelve la tabla fija de cuatro publicaciones, con fechas de 2020."""
    # Cada tupla es (id de la publicación, id del autor, hora)
    datos = [(1, 2, "09:00"), (2, 3, "10:00"), (3, 2, "11:00"), (4, 1, "12:00")]
    return [
        Publicacion(id_pub, autor, "texto", f"2020-01-01T{hora}:00+00:00")
        for id_pub, autor, hora in datos
    ]


def crear_servicio(amistades=None, publicaciones=None, repositorio=None):
    """
    Arma un servicio con piezas falsas y devuelve (servicio, repositorio, sesion).

    Si no se indican, usa las amistades de siempre (Ana y Beto son amigos), la
    tabla de ejemplo y a Ana con la sesión iniciada.
    """
    if repositorio is None:
        # Si no se pasa una lista, se usa la tabla de ejemplo
        if publicaciones is None:
            publicaciones = crear_publicaciones_de_ejemplo()
        repositorio = RepositorioPublicacionesEnMemoria(publicaciones)
    sesion = SesionFalsa()
    servicio = ServicioPublicaciones(
        repositorio, ConsultaAmistadesFalsa(amistades), DirectorioUsuariosFalso(), sesion
    )
    return servicio, repositorio, sesion


def ids(publicaciones: list[Publicacion]) -> list[int]:
    """Devuelve solo los ids de una lista de publicaciones, para comparar fácil."""
    return [p.id_publicacion for p in publicaciones]


# ---------------------------------------------------------------- publicar


def prueba_publicar_devuelve_la_publicacion_con_id_autor_y_texto():
    """Publicar crea la publicación 5, a nombre de Ana (id 1), con el texto recibido."""
    servicio, _, _ = crear_servicio()
    # Ejecutar: Ana publica un mensaje
    publicacion = servicio.publicar("Hola")
    # Comprobar: la tabla llega hasta el id 4, así que la nueva es la 5
    assert publicacion.id_publicacion == 5
    assert publicacion.id_autor == 1
    assert publicacion.texto == "Hola"


def prueba_publicar_guarda_en_el_repositorio():
    """Después de publicar, el repositorio tiene las cinco publicaciones y se guardó una vez."""
    servicio, repositorio, _ = crear_servicio()
    servicio.publicar("Hola")
    # Comprobar: las cuatro de antes más la nueva, con un solo guardado
    assert ids(repositorio.cargar_todo()) == [1, 2, 3, 4, 5]
    assert repositorio.veces_guardado == 1


def prueba_publicar_quita_los_espacios_de_los_bordes():
    """Los espacios al inicio y al final del texto no se guardan."""
    servicio, _, _ = crear_servicio()
    publicacion = servicio.publicar("   Hola   ")
    assert publicacion.texto == "Hola"


def prueba_publicar_asigna_la_fecha_actual_en_iso_utc():
    """La fecha de la publicación es la de ahora, en ISO 8601 con zona UTC."""
    servicio, _, _ = crear_servicio()
    publicacion = servicio.publicar("Hola")
    # Si el formato no fuera ISO 8601, fromisoformat lanzaría un error
    fecha = datetime.fromisoformat(publicacion.fecha_creacion)
    # Debe traer zona horaria (UTC) y estar a menos de un minuto de ahora
    assert fecha.tzinfo is not None
    assert abs((datetime.now(timezone.utc) - fecha).total_seconds()) < 60


def prueba_publicar_varias_veces_incrementa_los_ids():
    """Cada publicación nueva recibe el id siguiente, sin repetir."""
    servicio, _, _ = crear_servicio()
    primera = servicio.publicar("Una")
    segunda = servicio.publicar("Otra")
    assert (primera.id_publicacion, segunda.id_publicacion) == (5, 6)


def prueba_publicar_texto_vacio_lanza_error_y_no_guarda():
    """Un texto vacío es inválido y no se guarda nada."""
    servicio, repositorio, _ = crear_servicio()
    with pytest.raises(ErrorValidacion, match="vacía"):
        servicio.publicar("")
    # Si hubiera guardado algo, veces_guardado sería mayor que 0
    assert repositorio.veces_guardado == 0


def prueba_publicar_solo_espacios_lanza_error():
    """Un texto de solo espacios cuenta como vacío."""
    servicio, repositorio, _ = crear_servicio()
    with pytest.raises(ErrorValidacion, match="vacía"):
        servicio.publicar("     ")
    assert repositorio.veces_guardado == 0


def prueba_publicar_281_caracteres_lanza_error_y_no_guarda():
    """Un texto que pasa el máximo (280) por un carácter es inválido."""
    servicio, repositorio, _ = crear_servicio()
    texto_largo = "x" * (LARGO_MAXIMO_PUBLICACION + 1)
    # El mensaje de error menciona el máximo permitido
    with pytest.raises(ErrorValidacion, match="280"):
        servicio.publicar(texto_largo)
    assert repositorio.veces_guardado == 0


def prueba_publicar_280_caracteres_es_valido():
    """Un texto de exactamente 280 caracteres se acepta: el límite es inclusivo."""
    servicio, repositorio, _ = crear_servicio()
    publicacion = servicio.publicar("x" * LARGO_MAXIMO_PUBLICACION)
    assert len(publicacion.texto) == 280
    assert repositorio.veces_guardado == 1


def prueba_publicar_sin_sesion_lanza_error_de_autenticacion():
    """Sin un usuario con sesión iniciada no se puede publicar."""
    servicio, repositorio, sesion = crear_servicio()
    # Preparar: se cierra la sesión de Ana
    sesion.cerrar()
    with pytest.raises(ErrorAutenticacion):
        servicio.publicar("Hola")
    assert repositorio.veces_guardado == 0


def prueba_si_falla_el_guardado_la_publicacion_no_queda_en_memoria():
    """Se guarda primero en el archivo: si eso falla, la memoria queda igual que antes."""
    # Preparar: un repositorio que falla siempre al guardar
    repositorio = RepositorioQueFalla(crear_publicaciones_de_ejemplo())
    servicio, _, _ = crear_servicio(repositorio=repositorio)
    with pytest.raises(ErrorAlmacenamiento):
        servicio.publicar("Hola")
    # Comprobar: Ana sigue con una sola publicación (la 4), sin la nueva
    assert ids(servicio.obtener_muro_personal()) == [4]


# -------------------------------------------------------------------- muro


def prueba_muro_incluye_propias_y_de_amigos_mas_reciente_primero():
    """El muro de Ana tiene sus publicaciones y las de Beto, de la más reciente a la más antigua."""
    servicio, _, _ = crear_servicio()
    # Los autores del muro son {1, 2}: la 1 (Beto), la 3 (Beto) y la 4 (Ana)
    assert ids(servicio.obtener_muro()) == [4, 3, 1]


def prueba_muro_no_incluye_publicaciones_de_no_amigos():
    """Carla (id 3) no es amiga de Ana, así que su publicación 2 no aparece."""
    servicio, _, _ = crear_servicio()
    assert 2 not in ids(servicio.obtener_muro())


def prueba_muro_con_igual_fecha_desempata_por_id_mayor():
    """Si dos publicaciones tienen la misma fecha, va primero la de id mayor."""
    # Preparar: tres publicaciones de Ana con exactamente la misma fecha
    misma_fecha = "2020-01-01T09:00:00+00:00"
    publicaciones = [Publicacion(i, 1, "texto", misma_fecha) for i in (1, 2, 3)]
    servicio, _, _ = crear_servicio(publicaciones=publicaciones)
    assert ids(servicio.obtener_muro_personal()) == [3, 2, 1]


def prueba_muro_de_usuario_sin_amigos_solo_tiene_las_propias():
    """Carla no tiene amigos: su muro solo muestra su publicación."""
    servicio, _, sesion = crear_servicio()
    # Ejecutar: se inicia sesión como Carla (id 3)
    sesion.iniciar_como(USUARIOS_FALSOS[2])
    assert ids(servicio.obtener_muro()) == [2]


def prueba_muro_incluye_a_los_nuevos_amigos():
    """Si Ana agrega a Carla como amiga, las publicaciones de Carla aparecen en su muro."""
    # Preparar: ahora los amigos de Ana (id 1) son Beto (2) y Carla (3)
    servicio, _, _ = crear_servicio(amistades={1: {2, 3}})
    # Comprobar: aparece también la 2 (Carla), en su lugar cronológico
    assert ids(servicio.obtener_muro()) == [4, 3, 2, 1]


def prueba_muro_cambia_al_cambiar_de_usuario():
    """El servicio consulta la sesión en cada operación, así que el muro sigue al usuario activo."""
    servicio, _, sesion = crear_servicio()
    # Beto (id 2) es amigo de Ana (id 1): ve sus publicaciones y las de ella
    sesion.iniciar_como(USUARIOS_FALSOS[1])
    assert ids(servicio.obtener_muro()) == [4, 3, 1]
    # Carla (id 3) no tiene amigos: solo ve la suya
    sesion.iniciar_como(USUARIOS_FALSOS[2])
    assert ids(servicio.obtener_muro()) == [2]


def prueba_muro_personal_solo_tiene_las_del_usuario_activo():
    """El muro personal de Ana muestra únicamente sus publicaciones."""
    servicio, _, _ = crear_servicio()
    assert ids(servicio.obtener_muro_personal()) == [4]


def prueba_publicacion_nueva_aparece_primero_en_el_muro():
    """Lo que Ana publica ahora es lo más reciente, así que aparece arriba en su muro."""
    servicio, _, _ = crear_servicio()
    servicio.publicar("Hola")
    assert ids(servicio.obtener_muro()) == [5, 4, 3, 1]


def prueba_muro_sin_sesion_lanza_error_de_autenticacion():
    """Sin sesión iniciada no hay muro que mostrar."""
    servicio, _, sesion = crear_servicio()
    sesion.cerrar()
    with pytest.raises(ErrorAutenticacion):
        servicio.obtener_muro()


def prueba_un_servicio_nuevo_con_el_mismo_repositorio_ve_las_publicaciones_guardadas():
    """Simula cerrar y abrir la app: lo publicado antes se recupera del repositorio."""
    servicio, repositorio, sesion = crear_servicio()
    servicio.publicar("Hola")
    # Ejecutar: se crea un servicio nuevo con el mismo repositorio, como al reabrir la app
    servicio_nuevo = ServicioPublicaciones(
        repositorio, ConsultaAmistadesFalsa(), DirectorioUsuariosFalso(), sesion
    )
    # Comprobar: la publicación 5 sigue ahí
    assert ids(servicio_nuevo.obtener_muro()) == [5, 4, 3, 1]


def prueba_el_constructor_no_guarda_nada():
    """Crear el servicio solo carga el historial; no escribe en el repositorio."""
    _, repositorio, _ = crear_servicio()
    assert repositorio.veces_guardado == 0


# ----------------------------------------------------------- nombre del autor


def prueba_obtener_nombre_autor_devuelve_el_nombre_del_usuario():
    """Para el id 2 devuelve «Beto Rojas», que es como figura en el directorio."""
    servicio, _, _ = crear_servicio()
    assert servicio.obtener_nombre_autor(2) == "Beto Rojas"


def prueba_obtener_nombre_autor_de_id_inexistente_devuelve_usuario_desconocido():
    """Si el usuario ya no existe, la pantalla puede mostrar un texto en lugar de fallar."""
    servicio, _, _ = crear_servicio()
    assert servicio.obtener_nombre_autor(99) == "Usuario desconocido"