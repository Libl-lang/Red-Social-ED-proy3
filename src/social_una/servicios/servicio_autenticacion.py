import hashlib
import secrets
import logging
from datetime import datetime, timezone

from social_una.dominio.contratos import (
    DirectorioUsuarios,
    RepositorioUsuarios,
)
from social_una.dominio.errores import (
    ErrorAutenticacion,
    ErrorDuplicado,
    ErrorNoEncontrado,
    ErrorValidacion,
)
from social_una.dominio.modelos import Usuario
from social_una.estructuras.catalogo_usuarios import CatalogoUsuarios
from social_una.servicios.sesion import Sesion


class ServicioAutenticacion(DirectorioUsuarios):
    """Gestiona el registro, inicio y cierre de sesion."""

    ITERACIONES_HASH = 600000

    def __init__(
        self,
        repositorio: RepositorioUsuarios,
        sesion: Sesion,
        registrador: logging.Logger | None = None,
    ):
        self._repositorio = repositorio
        self._sesion = sesion
        self._catalogo = CatalogoUsuarios()
        self._registrador = registrador

        usuarios = self._repositorio.cargar_todo()

        for usuario in usuarios:
            self._catalogo.agregar(usuario)

    def _registrar_evento(self, nivel: str, mensaje: str) -> None:
        """Registra un evento si hay un registrador configurado."""

        if self._registrador is None:
            return

        if nivel == "warning":
            self._registrador.warning(mensaje)
        else:
            self._registrador.info(mensaje)

    def registrar(
        self,
        nombre: str,
        nombre_usuario: str,
        contrasena: str
    ) -> Usuario:
        """Registra un usuario nuevo y guarda sus datos."""

        nombre = nombre.strip()
        nombre_usuario = nombre_usuario.strip()

        if not nombre or not nombre_usuario or not contrasena:
            raise ErrorValidacion(
                "Todos los campos son obligatorios."
            )

        if len(contrasena) < 6:
            raise ErrorValidacion(
                "La contrasena debe tener al menos 6 caracteres."
            )

        if self._catalogo.buscar_por_nombre_usuario(nombre_usuario):
            raise ErrorDuplicado(
                "El nombre de usuario ya esta registrado."
            )

        sal = secrets.token_hex(16)

        hash_contrasena = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            sal.encode("utf-8"),
            self.ITERACIONES_HASH
        ).hex()

        usuario = Usuario(
            id_usuario=self._catalogo.siguiente_id(),
            nombre=nombre,
            nombre_usuario=nombre_usuario,
            hash_contrasena=hash_contrasena,
            sal=sal,
            fecha_registro=datetime.now(timezone.utc).isoformat()
        )

        usuarios_actualizados = self._catalogo.listar_todos()
        usuarios_actualizados.append(usuario)

        # Primero se guarda; luego se actualiza el catalogo en memoria.
        self._repositorio.guardar_todo(usuarios_actualizados)
        self._catalogo.agregar(usuario)

        self._registrar_evento(
            "info",
            f"Registro exitoso | ID usuario: {usuario.id_usuario}",
        )

        return usuario

    def iniciar_sesion(
        self,
        nombre_usuario: str,
        contrasena: str
    ) -> Usuario:
        """Verifica las credenciales e inicia la sesion."""

        if not nombre_usuario or not nombre_usuario.strip() or not contrasena:
            self._registrar_evento(
                "warning",
                "Inicio de sesion fallido | Datos incompletos",
            )
            raise ErrorAutenticacion(
                "Debe ingresar el usuario y la contrasena."
            )

        usuario = self._catalogo.buscar_por_nombre_usuario(
            nombre_usuario.strip()
        )

        if usuario is None:
            self._registrar_evento(
                "warning",
                "Inicio de sesion fallido | Usuario no encontrado",
            )
            raise ErrorAutenticacion(
                "El usuario o la contrasena son incorrectos."
            )

        hash_ingresado = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            usuario.sal.encode("utf-8"),
            self.ITERACIONES_HASH
        ).hex()

        if not secrets.compare_digest(
            hash_ingresado,
            usuario.hash_contrasena
        ):
            self._registrar_evento(
                "warning",
                "Inicio de sesion fallido | Credenciales incorrectas",
            )
            raise ErrorAutenticacion(
                "El usuario o la contrasena son incorrectos."
            )

        self._sesion.iniciar(usuario)

        self._registrar_evento(
            "info",
            f"Inicio de sesion exitoso | ID usuario: {usuario.id_usuario}",
        )

        return usuario

    def cerrar_sesion(self):
        """Cierra la sesion actual."""

        try:
            usuario = self._sesion.usuario_actual()
            id_usuario = usuario.id_usuario
        except ErrorAutenticacion:
            id_usuario = None

        self._sesion.cerrar()

        if id_usuario is not None:
            self._registrar_evento(
                "info",
                f"Cierre de sesion | ID usuario: {id_usuario}",
            )

    def obtener_por_id(self, id_usuario: int) -> Usuario:
        """Obtiene un usuario mediante su identificador."""

        usuario = self._catalogo.buscar_por_id(id_usuario)

        if usuario is None:
            raise ErrorNoEncontrado(
                "No se encontro el usuario solicitado."
            )

        return usuario

    def buscar(self, texto: str) -> list[Usuario]:
        """Busca usuarios por nombre o nombre de usuario."""

        return self._catalogo.buscar_por_texto(texto)

    def existe(self, id_usuario: int) -> bool:
        """Comprueba si existe un usuario con ese identificador."""

        return self._catalogo.buscar_por_id(id_usuario) is not None
