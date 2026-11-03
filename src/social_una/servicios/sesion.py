from social_una.dominio.modelos import Usuario

class Sesion:
    """Controla la sesion del usuario actual."""

    def __init__(self):
        self._usuario_actual = None

    def iniciar(self, usuario: Usuario):
        """Inicia la sesion de un usuario."""
        self._usuario_actual = usuario

    def cerrar(self):
        """Cierra la sesion actual."""
        self._usuario_actual = None

    def usuario_actual(self):
        """Devuelve el usuario que tiene la sesion activa."""
        return self._usuario_actual

    def hay_sesion_iniciada(self):
        """Indica si existe una sesion activa."""
        return self._usuario_actual is not None
