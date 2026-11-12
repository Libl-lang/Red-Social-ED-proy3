
"""
Servicio de publicaciones y muro de Social UNA.
---------------------------------------------------------------------------
Contiene la lógica para publicar mensajes y para armar el muro del usuario
activo. No lee ni escribe archivos por su cuenta: recibe el repositorio, la
consulta de amistades, el directorio de usuarios y la sesión como contratos
del dominio, así que funciona igual con piezas falsas o reales.

----------------------------------------------------------------------------
"""

import logging
from datetime import datetime, timezone

from social_una.dominio.contratos import (
    ConsultaAmistades,
    DirectorioUsuarios,
    RepositorioPublicaciones,
    SesionActiva,
)
from social_una.dominio.errores import ErrorNoEncontrado, ErrorValidacion
from social_una.dominio.modelos import Publicacion
from social_una.estructuras.historial_publicaciones import HistorialPublicaciones

LARGO_MAXIMO_PUBLICACION = 280


class ServicioPublicaciones:
    """Publica mensajes y arma el muro del usuario activo."""

    def __init__(
        self,
        repositorio: RepositorioPublicaciones,
        consulta_amistades: ConsultaAmistades,
        directorio: DirectorioUsuarios,
        sesion: SesionActiva,
        registrador: logging.Logger | None = None,
    ) -> None:
        self._repositorio = repositorio
        self._consulta_amistades = consulta_amistades
        self._directorio = directorio
        self._sesion = sesion
        self._registrador = registrador

        self._historial = HistorialPublicaciones(
            repositorio.cargar_todo()
        )

    def publicar(self, texto: str) -> Publicacion:
        """Publica un mensaje a nombre del usuario activo."""

        usuario = self._sesion.usuario_actual()

        texto_limpio = texto.strip()

        if texto_limpio == "":
            raise ErrorValidacion(
                "La publicación no puede estar vacía."
            )

        if len(texto_limpio) > LARGO_MAXIMO_PUBLICACION:
            raise ErrorValidacion(
                f"La publicación no puede superar los "
                f"{LARGO_MAXIMO_PUBLICACION} caracteres "
                f"(tiene {len(texto_limpio)})."
            )

        publicacion = Publicacion(
            id_publicacion=self._historial.siguiente_id(),
            id_autor=usuario.id_usuario,
            texto=texto_limpio,
            fecha_creacion=datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds"),
        )

        # Primero persistir; después actualizar la memoria.
        self._repositorio.guardar_todo(
            self._historial.listar_todas() + [publicacion]
        )

        self._historial.agregar(publicacion)

        # Registrar solamente los identificadores.
        if self._registrador is not None:
            self._registrador.info(
                f"Publicación creada | "
                f"ID publicación: {publicacion.id_publicacion} | "
                f"ID autor: {usuario.id_usuario}"
            )

        return publicacion

    def obtener_muro(self) -> list[Publicacion]:
        """Devuelve publicaciones propias y de amigos."""

        usuario = self._sesion.usuario_actual()

        ids_autores = (
            self._consulta_amistades.obtener_ids_amigos(
                usuario.id_usuario
            )
            | {usuario.id_usuario}
        )

        publicaciones = self._historial.obtener_de_autores(
            ids_autores
        )

        return self._ordenar_recientes(publicaciones)

    def obtener_muro_personal(self) -> list[Publicacion]:
        """Devuelve solamente las publicaciones del usuario activo."""

        usuario = self._sesion.usuario_actual()

        publicaciones = self._historial.obtener_por_autor(
            usuario.id_usuario
        )

        return self._ordenar_recientes(publicaciones)

    def obtener_nombre_autor(self, id_autor: int) -> str:
        """Devuelve el nombre del autor o un texto alternativo."""

        try:
            return self._directorio.obtener_por_id(id_autor).nombre
        except ErrorNoEncontrado:
            return "Usuario desconocido"

    @staticmethod
    def _ordenar_recientes(
        publicaciones: list[Publicacion],
    ) -> list[Publicacion]:
        """Ordena de la más reciente a la más antigua."""

        return sorted(
            publicaciones,
            key=lambda p: (
                p.fecha_creacion,
                p.id_publicacion,
            ),
            reverse=True,
        )
