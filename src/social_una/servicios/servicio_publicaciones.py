
"""
Servicio de publicaciones y muro.
---------------------------------------------------------------------------
Contiene la lógica para publicar mensajes y para armar el muro del usuario
activo. No lee ni escribe archivos por su cuenta: recibe el repositorio, la
consulta de amistades, el directorio de usuarios y la sesión como contratos
del dominio, así que funciona igual con piezas falsas o reales.

----------------------------------------------------------------------------
"""

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
    
    """
    Publica mensajes y arma el muro del usuario activo.
    ----------------------------------------------------------------------
    Guarda las publicaciones en un HistorialPublicaciones en memoria y las
    persiste con el repositorio después de cada publicación nueva.
    ---------------------------------------------------------------------

    """

    def __init__(
            
        self,
        repositorio: RepositorioPublicaciones,
        consulta_amistades: ConsultaAmistades,
        directorio: DirectorioUsuarios,
        sesion: SesionActiva,

    ) -> None:
        
        #Recibe las cuatro piezas que necesita y carga el historial guardado.

        self._repositorio = repositorio
        self._consulta_amistades = consulta_amistades
        self._directorio = directorio
        self._sesion = sesion

        # Al crear el servicio se reconstruye el historial desde el archivo
        self._historial = HistorialPublicaciones(repositorio.cargar_todo())

    def publicar(self, texto: str) -> Publicacion:

        """
        Publica un mensaje a nombre del usuario activo y lo devuelve.
        ---------------------------------------------------------------------
        Lanza ErrorValidacion si el texto está vacío o supera el largo máximo,
        y ErrorAutenticacion si no hay sesión iniciada.

        """
        # Si no hay sesión, usuario_actual() lanza ErrorAutenticacion y se propaga
        usuario = self._sesion.usuario_actual()

        # Se quitan los espacios de los bordes antes de validar
        texto_limpio = texto.strip()
        if texto_limpio == "":
            raise ErrorValidacion("La publicación no puede estar vacía.")
        if len(texto_limpio) > LARGO_MAXIMO_PUBLICACION:
            raise ErrorValidacion(
                f"La publicación no puede superar los {LARGO_MAXIMO_PUBLICACION} "
                f"caracteres (tiene {len(texto_limpio)})."
            )

        # Id nuevo y fecha actual en UTC, en formato ISO 8601
        publicacion = Publicacion(
            id_publicacion=self._historial.siguiente_id(),
            id_autor=usuario.id_usuario,
            texto=texto_limpio,
            fecha_creacion=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

        # Primero se guarda en el archivo: si falla, la memoria no queda con
        # una publicación que no existe en disco
        self._repositorio.guardar_todo(self._historial.listar_todas() + [publicacion])
        self._historial.agregar(publicacion)
        return publicacion

    def obtener_muro(self) -> list[Publicacion]:

        """Devuelve el muro: publicaciones propias y de amigos, de la más reciente a la más antigua."""

        usuario = self._sesion.usuario_actual()

        # El muro incluye al propio usuario además de sus amigos
        ids_autores = self._consulta_amistades.obtener_ids_amigos(usuario.id_usuario) | {
            usuario.id_usuario
        }
        publicaciones = self._historial.obtener_de_autores(ids_autores)
        return self._ordenar_recientes(publicaciones)

    def obtener_muro_personal(self) -> list[Publicacion]:
        """Devuelve solo las publicaciones del usuario activo, de la más reciente a la más antigua."""

        usuario = self._sesion.usuario_actual()
        publicaciones = self._historial.obtener_por_autor(usuario.id_usuario)
        return self._ordenar_recientes(publicaciones)

    def obtener_nombre_autor(self, id_autor: int) -> str:

        """Devuelve el nombre del autor, o «Usuario desconocido» si ya no existe."""

        try:
            return self._directorio.obtener_por_id(id_autor).nombre
        except ErrorNoEncontrado:
            return "Usuario desconocido"

    @staticmethod
    def _ordenar_recientes(publicaciones: list[Publicacion]) -> list[Publicacion]:

        """Ordena de la más reciente a la más antigua; con igual fecha, el id mayor primero."""

        # Las fechas ISO 8601 en UTC se ordenan correctamente como texto
        return sorted(
            publicaciones,
            key=lambda p: (p.fecha_creacion, p.id_publicacion),
            reverse=True,
        )