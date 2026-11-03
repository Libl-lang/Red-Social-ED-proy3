from social_una.dominio.contratos import SesionActiva
from social_una.dominio.errores import ErrorAutenticacion
from social_una.dominio.modelos import Usuario

class Sesion(SesionActiva):
    """Controla la sesion del usuario actual."""

    def __init__(self):
        self._usuario_actual = None

    def iniciar(self, usuario: Usuario):
        """Inicia la sesion de un usuario."""
        self._usuario_actual = usuario

    def cerrar(self):
        """Cierra la sesion actual."""
        self._usuario_actual = None

    def usuario_actual(self) -> Usuario:
        """Devuelve el usuario con la sesion iniciada."""

        if self._usuario_actual is None:
            raise ErrorAutenticacion(
                "No hay una sesion iniciada."
            )

        return self._usuario_actual

    def hay_sesion_iniciada(self) -> bool:
        """Indica si existe una sesion activa."""
        return self._usuario_actual is not None
