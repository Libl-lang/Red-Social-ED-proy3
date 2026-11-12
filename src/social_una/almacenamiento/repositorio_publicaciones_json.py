"""
Repositorio de publicaciones en archivo JSON.

Guarda y carga las publicaciones en publicaciones.json usando AlmacenJson
y cumple el contrato RepositorioPublicaciones definido en el dominio.
"""

from pathlib import Path

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.dominio.contratos import RepositorioPublicaciones
from social_una.dominio.errores import ErrorAlmacenamiento
from social_una.dominio.modelos import Publicacion


class RepositorioPublicacionesJson(RepositorioPublicaciones):
    """Gestiona la persistencia de publicaciones mediante JSON."""

    def __init__(
        self,
        ruta: str | Path,
        almacen: AlmacenJson
    ) -> None:
        self._ruta = Path(ruta)
        self._almacen = almacen

    def cargar_todo(self) -> list[Publicacion]:
        """Carga todas las publicaciones guardadas."""

        datos = self._almacen.leer(self._ruta, [])

        if not isinstance(datos, list):
            raise ErrorAlmacenamiento(
                f"El archivo {self._ruta} debe contener una lista."
            )

        if not all(isinstance(publicacion, dict) for publicacion in datos):
            raise ErrorAlmacenamiento(
                f"El archivo {self._ruta} contiene registros inválidos."
            )

        try:
            return [
                Publicacion.desde_diccionario(publicacion)
                for publicacion in datos
            ]

        except (KeyError, TypeError, ValueError) as error:
            raise ErrorAlmacenamiento(
                f"El archivo {self._ruta} contiene publicaciones "
                "incompletas o con datos inválidos."
            ) from error

    def guardar_todo(
        self,
        publicaciones: list[Publicacion]
    ) -> None:
        """Guarda la lista completa de publicaciones."""

        datos = [
            publicacion.a_diccionario()
            for publicacion in publicaciones
        ]

        self._almacen.escribir_seguro(
            self._ruta,
            datos
        )
