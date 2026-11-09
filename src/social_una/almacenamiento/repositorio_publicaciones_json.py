
"""
-------------------------------------------------------
Repositorio de publicaciones en archivo JSON.
-------------------------------------------------------

Guarda y carga las publicaciones en publicaciones.json usando AlmacenJson, y
cumple el contrato RepositorioPublicaciones definido en el dominio.

--------------------------------------------------------

"""

from pathlib import Path

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.dominio.contratos import RepositorioPublicaciones
from social_una.dominio.errores import ErrorAlmacenamiento
from social_una.dominio.modelos import Publicacion


class RepositorioPublicacionesJson(RepositorioPublicaciones):

    """
    Guarda y carga el historial de publicaciones en un archivo JSON.
    -------------------------------------------------------------------------
    El archivo contiene una lista con una publicación por elemento. La lectura
    y la escritura segura las hace AlmacenJson.
    -------------------------------------------------------------------------

    """

    def __init__(self, ruta: str | Path, almacen: AlmacenJson) -> None:

        """Recibe la ruta del archivo y el almacén que lo lee y lo escribe."""

        self._ruta = Path(ruta)
        self._almacen = almacen

    def cargar_todo(self) -> list[Publicacion]:

        """
        Devuelve las publicaciones guardadas en el archivo.
        -------------------------------------------------------------

        Si el archivo no existe devuelve una lista vacía. Lanza
        ErrorAlmacenamiento si el archivo está dañado, no es una lista o
        alguna publicación está incompleta o tiene datos inválidos.

        -------------------------------------------------------------
        """
        
        # 1) Lee el archivo; si no existe, AlmacenJson devuelve una lista vacía
        datos = self._almacen.leer(self._ruta, [])

        # 2) El contenido debe ser una lista de publicaciones
        if not isinstance(datos, list):

            raise ErrorAlmacenamiento(

                f"El archivo {self._ruta} no tiene el formato esperado: "
                "se esperaba una lista de publicaciones."

            )

        # 3) Convierte cada elemento en una Publicacion (los ids vuelven como enteros)
        try:
            return [Publicacion.desde_diccionario(d) for d in datos]
        
        except (KeyError, TypeError, ValueError) as error:

            raise ErrorAlmacenamiento(

                f"El archivo {self._ruta} tiene publicaciones incompletas "
                "o con datos inválidos."

            ) from error

    def guardar_todo(self, publicaciones: list[Publicacion]) -> None:

        """Guarda la lista completa de publicaciones, reemplazando lo anterior."""
        # Convierte cada Publicacion a diccionario y escribe de forma segura

        self._almacen.escribir_seguro(

            self._ruta, [p.a_diccionario() for p in publicaciones]

        )