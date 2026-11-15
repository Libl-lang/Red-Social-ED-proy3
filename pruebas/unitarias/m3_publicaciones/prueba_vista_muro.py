"""Pruebas del flujo de confirmación para eliminar publicaciones propias."""

from types import SimpleNamespace

from social_una.dominio.errores import ErrorNoEncontrado
from social_una.interfaz import alertas
from social_una.interfaz.vista_muro import VistaMuro


class _ServicioPublicacionesFalso:
    def __init__(self, error=None):
        self.error = error
        self.eliminadas = []

    def eliminar_publicacion(self, id_publicacion):
        if self.error is not None:
            raise self.error
        self.eliminadas.append(id_publicacion)


def _crear_vista(servicio):
    refrescos = []
    vista = SimpleNamespace(
        _servicio=servicio,
        refrescar=lambda: refrescos.append(True),
    )
    return vista, refrescos


def prueba_cancelar_eliminacion_de_publicacion_no_cambia_nada(monkeypatch):
    servicio = _ServicioPublicacionesFalso()
    vista, refrescos = _crear_vista(servicio)
    mensajes = []
    monkeypatch.setattr(alertas, "confirmar", lambda _pregunta: False)
    monkeypatch.setattr(
        alertas,
        "mostrar_informacion",
        lambda mensaje: mensajes.append(mensaje),
    )

    VistaMuro._al_eliminar_publicacion(vista, 7)

    assert servicio.eliminadas == []
    assert refrescos == []
    assert mensajes == []


def prueba_confirmar_eliminacion_de_publicacion_refresca_y_notifica(monkeypatch):
    servicio = _ServicioPublicacionesFalso()
    vista, refrescos = _crear_vista(servicio)
    mensajes = []
    monkeypatch.setattr(alertas, "confirmar", lambda _pregunta: True)
    monkeypatch.setattr(
        alertas,
        "mostrar_informacion",
        lambda mensaje: mensajes.append(mensaje),
    )

    VistaMuro._al_eliminar_publicacion(vista, 7)

    assert servicio.eliminadas == [7]
    assert refrescos == [True]
    assert mensajes == ["La publicación se eliminó correctamente."]


def prueba_error_al_eliminar_publicacion_se_muestra_y_refresca(monkeypatch):
    servicio = _ServicioPublicacionesFalso(
        ErrorNoEncontrado("No existe la publicación.")
    )
    vista, refrescos = _crear_vista(servicio)
    errores = []
    monkeypatch.setattr(alertas, "confirmar", lambda _pregunta: True)
    monkeypatch.setattr(
        alertas,
        "mostrar_error",
        lambda mensaje: errores.append(mensaje),
    )

    VistaMuro._al_eliminar_publicacion(vista, 7)

    assert errores == ["No existe la publicación."]
    assert refrescos == [True]
