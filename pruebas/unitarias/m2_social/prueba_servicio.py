"""
Pruebas unitarias para ServicioSocial (Modulo 2).

Usa piezas falsas para probar el servicio de forma aislada.
"""

from social_una.dominio.contratos import ConsultaAmistades
from social_una.dominio.errores import (
    ErrorAlmacenamiento,
    ErrorDuplicado,
    ErrorNoEncontrado,
    ErrorValidacion,
)
from social_una.dominio.modelos import Usuario
from social_una.almacenamiento.repositorio_amistades_json import RepositorioAmistadesJson
from social_una.servicios.servicio_social import ServicioSocial
from pruebas.falsos.directorio_usuarios_falso import DirectorioUsuariosFalso, USUARIOS_FALSOS
from pruebas.falsos.repositorios_en_memoria import RepositorioAmistadesEnMemoria
from pruebas.falsos.sesion_falsa import SesionFalsa


def _crear_servicio_con_datos(iniciales_amistades=None, usuario_activo=None):
    """Crea un ServicioSocial con piezas falsas para pruebas."""
    if iniciales_amistades is None:
        iniciales_amistades = []
    if usuario_activo is None:
        usuario_activo = USUARIOS_FALSOS[0]  # Ana Mora (id=1)

    directorio = DirectorioUsuariosFalso()
    sesion = SesionFalsa(usuario_inicial=usuario_activo)
    repositorio = RepositorioAmistadesEnMemoria(datos_iniciales=iniciales_amistades)
    servicio = ServicioSocial(repositorio, directorio, sesion)
    return servicio


def prueba_servicio_implementa_consulta_amistades():
    """ServicioSocial debe implementar ConsultaAmistades."""
    servicio = _crear_servicio_con_datos()
    assert isinstance(servicio, ConsultaAmistades)


def prueba_obtener_ids_amigos_devuelve_conjunto():
    """obtener_ids_amigos devuelve los ids de amigos del usuario."""
    servicio = _crear_servicio_con_datos(iniciales_amistades=[(1, 2), (1, 3)])
    amigos = servicio.obtener_ids_amigos(1)
    assert amigos == {2, 3}


def prueba_son_amigos_devuelve_verdadero_si_son_amigos():
    """son_amigos devuelve True si los usuarios son amigos."""
    servicio = _crear_servicio_con_datos(iniciales_amistades=[(1, 2)])
    assert servicio.son_amigos(1, 2) is True
    assert servicio.son_amigos(2, 1) is True

def prueba_agregar_amigo_valido():
    """agregar_amigo agrega la amistad y la guarda."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[],
        usuario_activo=USUARIOS_FALSOS[0],  # Ana (id=1)
    )
    servicio.agregar_amigo(2)  # Agregar a Beto
    assert servicio.son_amigos(1, 2) is True
    assert servicio.son_amigos(2, 1) is True
    # Verificar que se guardo en el repositorio
    assert servicio._repositorio.veces_guardado >= 1


def prueba_eliminar_amigo_conserva_usuarios_y_otras_amistades():
    """Eliminar una relación no afecta cuentas ni amistades distintas."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[(1, 2), (1, 3), (2, 3)],
    )
    directorio = servicio._directorio

    servicio.eliminar_amigo(2)

    assert servicio.son_amigos(1, 2) is False
    assert servicio.son_amigos(2, 1) is False
    assert servicio.son_amigos(1, 3) is True
    assert servicio.son_amigos(2, 3) is True
    assert directorio.existe(1) is True
    assert directorio.existe(2) is True
    assert directorio.obtener_por_id(1).id_usuario == 1
    assert directorio.obtener_por_id(2).id_usuario == 2
    assert servicio._repositorio._datos == [(1, 3), (2, 3)]


def prueba_eliminar_amigo_inexistente_no_guarda_cambios():
    """Eliminar una relación ausente genera un error de dominio."""
    servicio = _crear_servicio_con_datos(iniciales_amistades=[(1, 3)])
    guardados = servicio._repositorio.veces_guardado

    try:
        servicio.eliminar_amigo(2)
        assert False, "Debia lanzar ErrorNoEncontrado"
    except ErrorNoEncontrado as error:
        assert "no existe" in str(error)

    assert servicio.son_amigos(1, 3) is True
    assert servicio._repositorio.veces_guardado == guardados


def prueba_eliminar_amigo_revierte_grafo_si_falla_el_guardado():
    """Un error al persistir restaura la amistad en memoria."""
    servicio = _crear_servicio_con_datos(iniciales_amistades=[(1, 2)])

    def fallar_guardado(_pares):
        raise ErrorAlmacenamiento("No se pudo guardar.")

    servicio._repositorio.guardar_todo = fallar_guardado

    try:
        servicio.eliminar_amigo(2)
        assert False, "Debia propagar ErrorAlmacenamiento"
    except ErrorAlmacenamiento:
        pass

    assert servicio.son_amigos(1, 2) is True
    assert servicio.son_amigos(2, 1) is True


def prueba_eliminar_amigo_se_persiste_al_recargar_y_se_puede_agregar(tmp_path):
    """El JSON recargado refleja la eliminación y admite otra alta."""
    ruta = tmp_path / "amistades.json"
    repositorio = RepositorioAmistadesJson(ruta)
    repositorio.guardar_todo([(1, 2), (1, 3)])
    directorio = DirectorioUsuariosFalso()
    sesion = SesionFalsa(usuario_inicial=USUARIOS_FALSOS[0])

    servicio = ServicioSocial(repositorio, directorio, sesion)
    servicio.eliminar_amigo(2)
    servicio_recargado = ServicioSocial(repositorio, directorio, sesion)

    assert servicio_recargado.son_amigos(1, 2) is False
    assert servicio_recargado.son_amigos(2, 1) is False
    assert servicio_recargado.son_amigos(1, 3) is True

    servicio_recargado.agregar_amigo(2)
    servicio_final = ServicioSocial(repositorio, directorio, sesion)
    assert servicio_final.son_amigos(1, 2) is True


def prueba_agregar_amigo_a_si_mismo_lanza_error_validacion():
    """agregar_amigo con el mismo id lanza ErrorValidacion."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[],
        usuario_activo=USUARIOS_FALSOS[0],  # Ana (id=1)
    )
    try:
        servicio.agregar_amigo(1)
        assert False, "Debia lanzar ErrorValidacion"
    except ErrorValidacion as e:
        assert "ti mismo" in str(e)


def prueba_agregar_amigo_usuario_inexistente_lanza_error_no_encontrado():
    """agregar_amigo con id inexistente lanza ErrorValidacion."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[],
        usuario_activo=USUARIOS_FALSOS[0],  # Ana (id=1)
    )
    try:
        servicio.agregar_amigo(99)
        assert False, "Debia lanzar ErrorValidacion"
    except ErrorValidacion as e:
        assert "99" in str(e)


def prueba_agregar_amigo_ya_amigos_lanza_error_duplicado():
    """agregar_amigo cuando ya son amigos lanza ErrorDuplicado."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[(1, 2)],  # Ana y Beto ya son amigos
        usuario_activo=USUARIOS_FALSOS[0],  # Ana (id=1)
    )
    try:
        servicio.agregar_amigo(2)
        assert False, "Debia lanzar ErrorDuplicado"
    except ErrorDuplicado as e:
        assert "Ya eres amigo" in str(e)


def prueba_listar_mis_amigos_devuelve_usuarios():
    """listar_mis_amigos devuelve objetos Usuario completos."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[(1, 2), (1, 3)],
        usuario_activo=USUARIOS_FALSOS[0],  # Ana (id=1)
    )
    amigos = servicio.listar_mis_amigos()
    ids = [u.id_usuario for u in amigos]
    assert ids == [2, 3]  # ordenados por id
    assert all(isinstance(u, Usuario) for u in amigos)


def prueba_listar_mis_amigos_vacio_sin_amistades():
    """listar_mis_amigos devuelve lista vacia si no hay amistades."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[],
        usuario_activo=USUARIOS_FALSOS[0],  # Ana (id=1)
    )
    amigos = servicio.listar_mis_amigos()
    assert amigos == []

def prueba_son_amigos_devuelve_falso_si_no_son_amigos():
    """son_amigos devuelve False si no son amigos."""
    servicio = _crear_servicio_con_datos(iniciales_amistades=[(1, 2)])
    assert servicio.son_amigos(1, 3) is False


def prueba_buscar_usuarios_excluye_usuario_activo():
    """buscar_usuarios no debe incluir al usuario activo."""
    servicio = _crear_servicio_con_datos(usuario_activo=USUARIOS_FALSOS[0])
    resultados = servicio.buscar_usuarios("")
    ids = [r["usuario"].id_usuario for r in resultados]
    assert 1 not in ids


def prueba_buscar_usuarios_marca_quienes_ya_son_amigos():
    """buscar_usuarios debe marcar es_amigo=True para amigos existentes."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[(1, 2)],
        usuario_activo=USUARIOS_FALSOS[0],
    )
    resultados = servicio.buscar_usuarios("Beto")
    assert len(resultados) == 1
    assert resultados[0]["usuario"].id_usuario == 2
    assert resultados[0]["es_amigo"] is True


def prueba_buscar_usuarios_no_amigo_marca_falso():
    """buscar_usuarios marca es_amigo=False para no amigos."""
    servicio = _crear_servicio_con_datos(
        iniciales_amistades=[],
        usuario_activo=USUARIOS_FALSOS[0],
    )
    resultados = servicio.buscar_usuarios("Beto")
    assert len(resultados) == 1
    assert resultados[0]["es_amigo"] is False