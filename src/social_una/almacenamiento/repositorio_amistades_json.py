"""
Repositorio de amistades en JSON para Social UNA.

Lee y escribe la lista de pares de ids de amistad usando AlmacenJson,
que garantiza una escritura segura mediante archivo temporal.
"""

from pathlib import Path
from typing import Any

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.dominio.contratos import RepositorioAmistades


class RepositorioAmistadesJson(RepositorioAmistades):
    """Implementacion de RepositorioAmistades que persiste en amistad JSON."""

    def __init__(self, ruta_archivo: str | Path) -> None:
        """
        Inicializa el repositorio con la ruta del archivo de amistades.

        Args:
            ruta_archivo: Ruta al archivo amistades.json.
        """
        self._ruta = Path(ruta_archivo)
        self._almacen = AlmacenJson()

    def cargar_todo(self) -> list[tuple[int, int]]:
        """
        Devuelve la lista de pares (id_a, id_b) guardados.

        Si el archivo no existe, devuelve una lista vacia.
        Lanza ErrorAlmacenamiento si el archivo esta corrupto.
        """
        datos: Any = self._almacen.leer(self._ruta, [])
        pares: list[tuple[int, int]] = []
        for par in datos:
            pares.append((int(par[0]), int(par[1])))
        # Ordenar para salida determinista
        pares.sort()
        return pares

    def guardar_todo(self, pares: list[tuple[int, int]]) -> None:
        """
        Guarda la lista completa de pares, reemplazando lo anterior.

        Los ids se convierten a enteros antes de guardar para garantizar
        consistencia en el archivo JSON.
        """
        datos_guardar = [[int(p[0]), int(p[1])] for p in pares]
        self._almacen.escribir_seguro(self._ruta, datos_guardar)
