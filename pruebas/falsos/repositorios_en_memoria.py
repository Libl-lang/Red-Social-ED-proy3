"""Piezas falsas para repositorios en memoria.

Clases que guardan datos en lista en memoria en lugar de archivos."""

from social_una.dominio.contratos import RepositorioAmistades, RepositorioPublicaciones, RepositorioUsuarios
from social_una.dominio.modelos import Publicacion, Usuario


class RepositorioUsuariosEnMemoria(RepositorioUsuarios):
    """Repositorio de usuarios en memoria."""

    def __init__(self, datos_iniciales: list | None = None):
        self._datos = list(datos_iniciales) if datos_iniciales is not None else []
        self.veces_guardado = 0

    def cargar_todo(self) -> list[Usuario]:
        """Devuelve una copia (list self._datos)."""
        return list(self._datos)

    def guardar_todo(self, usuarios: list[Usuario]) -> None:
        """Guarda una copia de la lista recibida y suma 1 a veces_guardado."""
        self._datos = list(usuarios)
        self.veces_guardado += 1


class RepositorioAmistadesEnMemoria(RepositorioAmistades):
    """Repositorio de amistades en memoria."""

    def __init__(self, datos_iniciales: list | None = None):
        self._datos = list(datos_iniciales) if datos_iniciales is not None else []
        self.veces_guardado = 0

    def cargar_todo(self) -> list[tuple[int, int]]:
        """Devuelve una copia (list self._datos)."""
        return list(self._datos)

    def guardar_todo(self, pares: list[tuple[int, int]]) -> None:
        """Guarda una copia de la lista recibida y suma 1 a veces_guardado."""
        self._datos = list(pares)
        self.veces_guardado += 1


class RepositorioPublicacionesEnMemoria(RepositorioPublicaciones):
    """Repositorio de publicaciones en memoria."""

    def __init__(self, datos_iniciales: list | None = None):
        self._datos = list(datos_iniciales) if datos_iniciales is not None else []
        self.veces_guardado = 0

    def cargar_todo(self) -> list[Publicacion]:
        """Devuelve una copia (list self._datos)."""
        return list(self._datos)

    def guardar_todo(self, publicaciones: list[Publicacion]) -> None:
        """Guarda una copia de la lista recibida y suma 1 a veces_guardado."""
        self._datos = list(publicaciones)
        self.veces_guardado += 1
