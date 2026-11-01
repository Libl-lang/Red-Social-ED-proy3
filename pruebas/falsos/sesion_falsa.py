"""Pieza falsa para SesionActiva.

Proporciona una sesión simulada con un usuario fijo para las pruebas unitarias."""

from social_una.dominio.contratos import SesionActiva
from social_una.dominio.errores import ErrorAutenticacion
from social_una.dominio.modelos import Usuario
from pruebas.falsos.directorio_usuarios_falso import USUARIOS_FALSOS


class SesionFalsa(SesionActiva):
    """Implementación falsa de SesionActiva para pruebas."""

    def __init__(self, usuario_inicial: Usuario | None = USUARIOS_FALSOS[0]):
        self._usuario = usuario_inicial

    def usuario_actual(self) -> Usuario:
        if self._usuario is None:
            raise ErrorAutenticacion("No hay ninguna sesión iniciada.")
        return self._usuario

    def hay_sesion_iniciada(self) -> bool:
        return self._usuario is not None

    def iniciar_como(self, usuario: Usuario) -> None:
        self._usuario = usuario

    def cerrar(self) -> None:
        self._usuario = None
