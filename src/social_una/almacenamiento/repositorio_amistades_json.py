"""
Repositorio de amistades en JSON para Social UNA.

Lee y escribe la lista de pares de ids de amistad usando AlmacenJson,
que garantiza una escritura segura mediante archivo temporal.
"""

from pathlib import Path
from typing import Any

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.dominio.contratos import RepositorioAmistades
from social_una.dominio.errores import ErrorAlmacenamiento


class RepositorioAmistadesJson(RepositorioAmistades):
    """Implementacion de RepositorioAmistades mediante JSON."""

    def __init__(self, ruta_archivo: str | Path) -> None:
        self._ruta = Path(ruta_archivo)
        self._almacen = AlmacenJson()

    def cargar_todo(self) -> list[tuple[int, int]]:
        """Carga los pares de identificadores de amistad."""

        datos: Any = self._almacen.leer(self._ruta, [])

        if not isinstance(datos, list):
            raise ErrorAlmacenamiento(
                "El archivo de amistades tiene un formato incorrecto."
            )

        pares = []

        try:
            for par in datos:
                if (
                    not isinstance(par, list)
                    or len(par) != 2
                    or any(
                        isinstance(identificador, bool)
                        for identificador in par
                    )
                ):
                    raise ValueError("Par de amistad invalido.")

                id_a = int(par[0])
                id_b = int(par[1])

                pares.append((id_a, id_b))

            pares.sort()
            return pares

        except (TypeError, ValueError, IndexError):
            raise ErrorAlmacenamiento(
                "El archivo de amistades contiene datos invalidos."
            )

    def guardar_todo(
        self,
        pares: list[tuple[int, int]]
    ) -> None:
        """Guarda la lista completa de pares de amistad."""

        try:
            datos_guardar = []

            for par in pares:
                if (
                    not isinstance(par, (tuple, list))
                    or len(par) != 2
                    or any(
                        isinstance(identificador, bool)
                        for identificador in par
                    )
                ):
                    raise ValueError("Par de amistad invalido.")

                datos_guardar.append([
                    int(par[0]),
                    int(par[1])
                ])

            self._almacen.escribir_seguro(
                self._ruta,
                datos_guardar
            )

        except (TypeError, ValueError, IndexError):
            raise ErrorAlmacenamiento(
                "No se pudieron guardar los datos de amistades."
            )
