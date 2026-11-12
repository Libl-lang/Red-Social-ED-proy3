"""
Servicio social de Social UNA (Modulo 2).

Implementa el contrato ConsultaAmistades y ofrece operaciones para
buscar usuarios, agregar amigos y listar los amigos del usuario activo.
"""

import logging

from social_una.almacenamiento.repositorio_amistades_json import (
    RepositorioAmistadesJson,
)
from social_una.dominio.contratos import (
    ConsultaAmistades,
    DirectorioUsuarios,
    SesionActiva,
)
from social_una.dominio.errores import (
    ErrorDuplicado,
    ErrorNoEncontrado,
    ErrorValidacion,
)
from social_una.dominio.modelos import Usuario
from social_una.estructuras.grafo_amistades import GrafoAmistades


class ServicioSocial(ConsultaAmistades):
    """Gestiona las amistades y la interacción social entre usuarios."""

    def __init__(
        self,
        repositorio: RepositorioAmistadesJson,
        directorio: DirectorioUsuarios,
        sesion: SesionActiva,
        registrador: logging.Logger | None = None,
    ) -> None:
        self._repositorio = repositorio
        self._directorio = directorio
        self._sesion = sesion
        self._registrador = registrador
        self._grafo = GrafoAmistades()

        self._cargar_amistades()

    def _registrar_evento(self, mensaje: str) -> None:
        """Registra un evento sin interrumpir la operacion social."""

        if self._registrador is None:
            return

        try:
            self._registrador.info(mensaje)
        except OSError:
            # Un fallo del registro no debe interrumpir el servicio.
            pass

    def _cargar_amistades(self) -> None:
        """Carga las amistades desde el repositorio al grafo."""

        pares = self._repositorio.cargar_todo()
        self._grafo.cargar_pares(pares)

    def _guardar_amistades(self) -> None:
        """Guarda las amistades actuales en el repositorio."""

        pares = self._grafo.exportar_pares()
        self._repositorio.guardar_todo(pares)

    def _usuario_actual(self) -> Usuario:
        """Devuelve el usuario con sesion iniciada."""

        return self._sesion.usuario_actual()

    # --- Implementacion de ConsultaAmistades ---

    def obtener_ids_amigos(self, id_usuario: int) -> set[int]:
        """Devuelve los IDs de amigos del usuario indicado."""

        return self._grafo.obtener_amigos(id_usuario)

    def son_amigos(self, id_a: int, id_b: int) -> bool:
        """Indica si dos usuarios son amigos."""

        return self._grafo.son_amigos(id_a, id_b)

    # --- Funcionalidades propias de M2 ---

    def buscar_usuarios(self, texto: str) -> list[dict]:
        """
        Busca usuarios por nombre o nombre de usuario.

        Excluye al usuario activo y marca quienes ya son amigos.
        """

        usuario_activo = self._usuario_actual()
        resultados = self._directorio.buscar(texto)

        lista: list[dict] = []

        for usuario in resultados:
            if usuario.id_usuario == usuario_activo.id_usuario:
                continue

            lista.append(
                {
                    "usuario": usuario,
                    "es_amigo": self._grafo.son_amigos(
                        usuario_activo.id_usuario,
                        usuario.id_usuario,
                    ),
                }
            )

        return lista

    def agregar_amigo(self, id_amigo: int) -> None:

        """Agrega al usuario indicado como amigo del usuario activo.

        Valida que no sea el propio usuario, que exista y que
        no sean amigos previamente. Si falla el guardado, revierte
        el cambio realizado en memoria.
        """

        usuario_activo = self._usuario_actual()
        id_activo = usuario_activo.id_usuario

        if id_amigo == id_activo:
            raise ErrorValidacion(
                "No puedes agregarte a ti mismo como amigo."
            )

        self._directorio.obtener_por_id(id_amigo)

        if self._grafo.son_amigos(id_activo, id_amigo):
            raise ErrorDuplicado(
                f"Ya eres amigo del usuario con id {id_amigo}."
            )

        # Agregar temporalmente la amistad al grafo.
        self._grafo.agregar_amistad(id_activo, id_amigo)

        try:
            # Guardar los cambios en el archivo JSON.
            self._guardar_amistades()

        except Exception:
            # Si falla el guardado, reconstruir el grafo sin esa amistad.
            pares_actuales = self._grafo.exportar_pares()

            pares_actuales.remove(
                (min(id_activo, id_amigo), max(id_activo, id_amigo))
            )

            self._grafo.cargar_pares(pares_actuales)

            raise

        self._registrar_evento(
            f"Amistad agregada | Usuario: {id_activo} | "
            f"Nuevo amigo: {id_amigo}"
        )

    def listar_mis_amigos(self) -> list[Usuario]:
        """Devuelve los objetos Usuario de los amigos del usuario activo."""

        usuario_activo = self._usuario_actual()
        ids_amigos = self._grafo.obtener_amigos(usuario_activo.id_usuario)