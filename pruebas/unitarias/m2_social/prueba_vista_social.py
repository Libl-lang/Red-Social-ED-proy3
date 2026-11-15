"""Pruebas del flujo de confirmación para eliminar amistades en la interfaz."""

from types import SimpleNamespace

from social_una.dominio.errores import ErrorNoEncontrado
from social_una.dominio.modelos import Usuario
from social_una.interfaz import vista_social


class _ServicioSocialFalso:
    def __init__(self, error=None):
        self.error = error
        self.eliminados = []

    def eliminar_amigo(self, id_amigo):
        if self.error is not None:
            raise self.error
        self.eliminados.append(id_amigo)


def _crear_vista_falsa(servicio):
    busquedas = []
    refrescos = []
    vista = SimpleNamespace(
        _servicio=servicio,
        _entrada_busqueda=SimpleNamespace(get=lambda: "Beto"),
        _mostrar_resultados=busquedas.append,
        _refrescar_amigos=lambda: refrescos.append(True),
    )
    return vista, busquedas, refrescos


def prueba_cancelar_eliminacion_no_cambia_nada(monkeypatch):
    servicio = _ServicioSocialFalso()
    vista, busquedas, refrescos = _crear_vista_falsa(servicio)
    mensajes = []
    monkeypatch.setattr(vista_social, "confirmar", lambda _pregunta: False)
    monkeypatch.setattr(
        vista_social,
        "mostrar_informacion",
        lambda mensaje: mensajes.append(mensaje),
    )
    monkeypatch.setattr(
        vista_social,
        "mostrar_error",
        lambda mensaje: mensajes.append(mensaje),
    )

    vista_social.VistaSocial._al_eliminar_amigo(
        vista,
        Usuario(2, "Beto Rojas", "beto", "hash", "sal", "fecha"),
    )

    assert servicio.eliminados == []
    assert busquedas == []
    assert refrescos == []
    assert mensajes == []


def prueba_confirmar_eliminacion_actualiza_listas_y_muestra_exito(monkeypatch):
    servicio = _ServicioSocialFalso()
    vista, busquedas, refrescos = _crear_vista_falsa(servicio)
    mensajes = []
    preguntas = []
    monkeypatch.setattr(
        vista_social,
        "confirmar",
        lambda pregunta: preguntas.append(pregunta) or True,
    )
    monkeypatch.setattr(
        vista_social,
        "mostrar_informacion",
        lambda mensaje: mensajes.append(mensaje),
    )

    vista_social.VistaSocial._al_eliminar_amigo(
        vista,
        Usuario(2, "Beto Rojas", "beto", "hash", "sal", "fecha"),
    )

    assert preguntas == ["¿Deseas eliminar a Beto Rojas de tus amistades?"]
    assert servicio.eliminados == [2]
    assert mensajes == ["Beto Rojas se eliminó de tu lista de amistades."]
    assert busquedas == ["Beto"]
    assert refrescos == [True]


def prueba_amistad_ya_eliminada_refresca_listas_y_muestra_error(monkeypatch):
    servicio = _ServicioSocialFalso(
        ErrorNoEncontrado("La amistad ya no existe.")
    )
    vista, busquedas, refrescos = _crear_vista_falsa(servicio)
    errores = []
    monkeypatch.setattr(vista_social, "confirmar", lambda _pregunta: True)
    monkeypatch.setattr(
        vista_social,
        "mostrar_error",
        lambda mensaje: errores.append(mensaje),
    )

    vista_social.VistaSocial._al_eliminar_amigo(
        vista,
        Usuario(2, "Beto Rojas", "beto", "hash", "sal", "fecha"),
    )

    assert errores == ["La amistad ya no existe."]
    assert busquedas == ["Beto"]
    assert refrescos == [True]
