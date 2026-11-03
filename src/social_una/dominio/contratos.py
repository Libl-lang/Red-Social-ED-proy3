"""Contratos entre módulos de Social UNA.

Define la lista de métodos que una pieza debe ofrecer a las otras, con sus
parámetros y lo que devuelve. No tiene lógica: cada módulo escribe la suya
heredando del contrato con los nombres exactos. Si a una clase le falta un
método del contrato, Python avisa al construirla."""

from abc import ABC, abstractmethod
from .modelos import Publicacion, Usuario


class DirectorioUsuarios(ABC):
    """Consulta de usuarios registrados. La implementa M1 (ServicioAutenticacion).
    La usan M2, para el buscador y para validar que un amigo exista, y M3,
    para mostrar el nombre del autor."""

    @abstractmethod
    def obtener_por_id(self, id_usuario: int) -> Usuario:
        """recibe el id de un usuario y devuelve su Usuario;
        lanza ErrorNoEncontrado si no existe ningún usuario con ese id."""

    @abstractmethod
    def buscar(self, texto: str) -> list[Usuario]:
        """recibe un texto y devuelve la lista de usuarios cuyo nombre o
        nombre de usuario lo contiene, ordenada por nombre y sin distinguir
        mayúsculas ni tildes; devuelve una lista vacía si no hay coincidencias."""

    @abstractmethod
    def existe(self, id_usuario: int) -> bool:
        """recibe un id y devuelve True si existe un usuario con ese id."""


class SesionActiva(ABC):
    """Información de quién tiene la sesión iniciada. La implementa M1 (Sesion).
    La usan M2 y M3 para saber cuál es el usuario activo. Se debe consultar
    en cada operación, no guardar el usuario al construir el servicio, porque
    la sesión puede cambiar."""

    @abstractmethod
    def usuario_actual(self) -> Usuario:
        """no recibe nada y devuelve el Usuario con la sesión iniciada;
        lanza ErrorAutenticacion si nadie ha iniciado sesión."""

    @abstractmethod
    def hay_sesion_iniciada(self) -> bool:
        """no recibe nada y devuelve True si hay un usuario con sesión
        iniciada."""


class ConsultaAmistades(ABC):
    """Consulta de la red de amistades. La implementa M2 (ServicioSocial).
    La usa M3 para armar el muro con las publicaciones del usuario y las de
    sus amigos."""

    @abstractmethod
    def obtener_ids_amigos(self, id_usuario: int) -> set[int]:
        """recibe el id de un usuario y devuelve el conjunto de ids de sus
        amigos; devuelve un conjunto vacío si no tiene amigos."""

    @abstractmethod
    def son_amigos(self, id_a: int, id_b: int) -> bool:
        """recibe dos ids y devuelve True si los dos usuarios son amigos."""


class RepositorioUsuarios(ABC):
    """Lectura y escritura de usuarios.json. La implementa M1 (RepositorioUsuariosJson).
    La usa ServicioAutenticacion para cargar los usuarios al abrir la app y
    guardarlos tras cada cambio."""

    @abstractmethod
    def cargar_todo(self) -> list[Usuario]:
        """devuelve la lista de usuarios guardados, o una lista vacía si el
        archivo no existe; lanza ErrorAlmacenamiento si el archivo está
        corrupto."""

    @abstractmethod
    def guardar_todo(self, usuarios: list[Usuario]) -> None:
        """recibe la lista completa de usuarios y la guarda, reemplazando lo
        anterior."""


class RepositorioAmistades(ABC):
    """Lectura y escritura de amistades.json. La implementa M2 (RepositorioAmistadesJson).
    La usa ServicioSocial para cargar las amistades al abrir la app y guardarlas
    tras cada cambio. Cada amistad se representa como un par de ids enteros."""

    @abstractmethod
    def cargar_todo(self) -> list[tuple[int, int]]:
        """devuelve la lista de pares (id_a, id_b) guardados, o una lista
        vacía si el archivo no existe; lanza ErrorAlmacenamiento si está
        corrupto."""

    @abstractmethod
    def guardar_todo(self, pares: list[tuple[int, int]]) -> None:
        """recibe la lista completa de pares y la guarda, reemplazando lo
        anterior."""


class RepositorioPublicaciones(ABC):
    """Lectura y escritura de publicaciones.json. La implementa M3 (RepositorioPublicacionesJson).
    La usa ServicioPublicaciones para cargar el historial al abrir la app y
    guardarlo tras cada cambio."""

    @abstractmethod
    def cargar_todo(self) -> list[Publicacion]:
        """devuelve la lista de publicaciones guardadas, o una lista vacía si
        el archivo no existe; lanza ErrorAlmacenamiento si está corrupto."""

    @abstractmethod
    def guardar_todo(self, publicaciones: list[Publicacion]) -> None:
        """recibe la lista completa de publicaciones y la guarda, reemplazando
        lo anterior."""
