from pathlib import Path

from social_una.dominio.contratos import RepositorioUsuarios
from social_una.dominio.errores import ErrorAlmacenamiento
from social_una.dominio.modelos import Usuario
from social_una.almacenamiento.almacen_json import AlmacenJson

class RepositorioUsuariosJson(RepositorioUsuarios):
    """Gestiona la persistencia de usuarios mediante archivos JSON."""

    def __init__(
        self,
        almacen: AlmacenJson,
        ruta: str | Path = "datos/usuarios.json"
    ):
        self._almacen = almacen
        self._ruta = Path(ruta)

    def cargar_todo(self) -> list[Usuario]:
        """Carga los usuarios guardados en el archivo JSON."""

        datos = self._almacen.leer(self._ruta, [])

        if not isinstance(datos, list):
            raise ErrorAlmacenamiento(
                "El archivo de usuarios tiene un formato incorrecto."
            )

        if not all(isinstance(usuario, dict) for usuario in datos):
            raise ErrorAlmacenamiento(
                "El archivo de usuarios contiene registros inválidos."
            )

        try:
            return [
                Usuario.desde_diccionario(usuario)
                for usuario in datos
            ]
        except (KeyError, TypeError, ValueError):
            raise ErrorAlmacenamiento(
                "El archivo de usuarios contiene datos inválidos."
            )

    def guardar_todo(self, usuarios: list[Usuario]) -> None:
        """Guarda la lista completa de usuarios en formato JSON."""

        datos = [
            usuario.a_diccionario()
            for usuario in usuarios
        ]

        self._almacen.escribir_seguro(self._ruta, datos)
