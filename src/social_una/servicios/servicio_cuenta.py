"""Operaciones coordinadas de cuenta y datos relacionados."""

import logging
from pathlib import Path

from social_una.almacenamiento.transaccion_json import (
    guardar_json_transaccional,
    recuperar_transaccion_json,
)
from social_una.dominio.contratos import (
    RepositorioAmistades,
    RepositorioPublicaciones,
    RepositorioUsuarios,
    SesionActiva,
)
from social_una.dominio.errores import (
    ErrorAlmacenamiento,
    ErrorNoEncontrado,
)
from social_una.servicios.servicio_autenticacion import ServicioAutenticacion
from social_una.servicios.servicio_publicaciones import ServicioPublicaciones
from social_una.servicios.servicio_social import ServicioSocial


class ServicioCuenta:
    """Coordina la eliminación de una cuenta autenticada y sus datos."""

    def __init__(
        self,
        directorio_datos: str | Path,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_amistades: RepositorioAmistades,
        repositorio_publicaciones: RepositorioPublicaciones,
        autenticacion: ServicioAutenticacion,
        social: ServicioSocial,
        publicaciones: ServicioPublicaciones,
        sesion: SesionActiva,
        registrador: logging.Logger | None = None,
    ) -> None:
        self._directorio_datos = Path(directorio_datos)
        self._repositorio_usuarios = repositorio_usuarios
        self._repositorio_amistades = repositorio_amistades
        self._repositorio_publicaciones = repositorio_publicaciones
        self._autenticacion = autenticacion
        self._social = social
        self._publicaciones = publicaciones
        self._sesion = sesion
        self._registrador = registrador

    def eliminar_mi_cuenta(self, contrasena_actual: str) -> None:
        """Elimina la cuenta activa mediante una transacción recuperable."""
        recuperar_transaccion_json(self._directorio_datos)
        usuario = self._sesion.usuario_actual()
        self._autenticacion.verificar_contrasena_actual(contrasena_actual)

        usuarios = self._repositorio_usuarios.cargar_todo()
        amistades = self._repositorio_amistades.cargar_todo()
        publicaciones = self._repositorio_publicaciones.cargar_todo()

        if not any(
            elemento.id_usuario == usuario.id_usuario
            for elemento in usuarios
        ):
            raise ErrorNoEncontrado(
                "La cuenta ya no existe en el archivo de usuarios."
            )
        if not self._autenticacion.existe(usuario.id_usuario):
            raise ErrorNoEncontrado(
                "La cuenta ya no existe en el catálogo de usuarios."
            )

        ids_usuarios = {elemento.id_usuario for elemento in usuarios}
        if any(
            id_a not in ids_usuarios or id_b not in ids_usuarios
            for id_a, id_b in amistades
        ):
            raise ErrorAlmacenamiento(
                "No se puede eliminar la cuenta porque amistades.json "
                "contiene referencias a usuarios inexistentes."
            )
        if any(
            publicacion.id_autor not in ids_usuarios
            for publicacion in publicaciones
        ):
            raise ErrorAlmacenamiento(
                "No se puede eliminar la cuenta porque publicaciones.json "
                "contiene autores inexistentes."
            )

        id_usuario = usuario.id_usuario
        usuarios_restantes = [
            elemento
            for elemento in usuarios
            if elemento.id_usuario != id_usuario
        ]
        amistades_restantes = [
            (id_a, id_b)
            for id_a, id_b in amistades
            if id_a != id_usuario and id_b != id_usuario
        ]
        publicaciones_restantes = [
            publicacion
            for publicacion in publicaciones
            if publicacion.id_autor != id_usuario
        ]

        guardar_json_transaccional(
            self._directorio_datos,
            {
                "usuarios.json": [
                    elemento.a_diccionario()
                    for elemento in usuarios_restantes
                ],
                "amistades.json": [
                    [id_a, id_b]
                    for id_a, id_b in amistades_restantes
                ],
                "publicaciones.json": [
                    elemento.a_diccionario()
                    for elemento in publicaciones_restantes
                ],
            },
        )

        self._social.actualizar_amistades_en_memoria(
            amistades_restantes
        )
        self._publicaciones.actualizar_historial_en_memoria(
            publicaciones_restantes
        )
        self._autenticacion.eliminar_usuario_de_memoria(id_usuario)
        self._registrar_evento(id_usuario)

    def _registrar_evento(self, id_usuario: int) -> None:
        if self._registrador is None:
            return
        try:
            self._registrador.info(
                "Cuenta eliminada y archivos sincronizados | "
                f"ID usuario: {id_usuario}"
            )
        except OSError:
            pass
