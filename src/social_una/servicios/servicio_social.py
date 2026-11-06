"""
Servicio social de Social UNA (Modulo 2).

Implementa el contrato ConsultaAmistades y ofrece operaciones para buscar
usuarios, agregar amigos y listar los amigos del usuario activo.

El servicio consulta el usuario actual en cada operacion mediante
usuario_actual() de la sesion activa y guarda los cambios usando el
repositorio de amistades.
"""

from social_una.almacenamiento.repositorio_amistades_json import (
    RepositorioAmistadesJson,
)
from social_una.dominio.contratos import ConsultaAmistades, DirectorioUsuarios, SesionActiva
from social_una.dominio.errores import ErrorDuplicado, ErrorNoEncontrado, ErrorValidacion
from social_una.dominio.modelos import Usuario
from social_una.estructuras.grafo_amistades import GrafoAmistades


class ServicioSocial(ConsultaAmistades):
    """
    Gestiona las amistades y la interaccion social entre usuarios.

    Implementa ConsultaAmistades. Usa un GrafoAmistades internamente para
    mantener la red de amistades y un RepositorioAmistadesJson para
    persistir los datos.
    """

    def __init__(
        self,
        repositorio: RepositorioAmistadesJson,
        directorio: DirectorioUsuarios,
        sesion: SesionActiva,
    ) -> None:
        """
        Inicializa el servicio social.

        Args:
            repositorio: Repositorio de amistades para persistencia.
            directorio: Directorio de usuarios para validar existencia y buscar.
            sesion: Sesion activa para obtener el usuario actual.
        """
        self._repositorio = repositorio
        self._directorio = directorio
        self._sesion = sesion
        self._grafo = GrafoAmistades()
        # Cargar amistades al iniciar
        self._cargar_amistades()

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
        """
        Devuelve el conjunto de ids de amigos del usuario dado.

        Implementa el contrato ConsultaAmistades.
        """
        return self._grafo.obtener_amigos(id_usuario)

    def son_amigos(self, id_a: int, id_b: int) -> bool:
        """
        Devuelve True si los dos usuarios son amigos.

        Implementa el contrato ConsultaAmistades.
        """
        return self._grafo.son_amigos(id_a, id_b)

    # --- Funcionalidades propias de M2 ---

    def buscar_usuarios(self, texto: str) -> list[dict]:
        """
        Busca usuarios cuyo nombre o nombre de usuario contenga el texto dado.

        Filtra usando el directorio de usuarios recibido. Excluye al usuario
        activo y marca quienes ya son amigos.

        Args:
            texto: Texto de busqueda.

        Returns:
            Lista de diccionarios con claves: usuario (Usuario), es_amigo (bool).
        """
        usuario_activo = self._usuario_actual()
        resultados = self._directorio.buscar(texto)

        lista: list[dict] = []
        for u in resultados:
            if u.id_usuario == usuario_activo.id_usuario:
                continue
            lista.append(
                {
                    "usuario": u,
                    "es_amigo": self._grafo.son_amigos(
                        usuario_activo.id_usuario, u.id_usuario
                    ),
                }
            )
        return lista

    def agregar_amigo(self, id_amigo: int) -> None:
        """
        Agrega a un usuario como amigo del usuario activo.

        Valida que:
        - No se intente agregarse a uno mismo (ErrorValidacion).
        - El usuario exista en el directorio (ErrorNoEncontrado).
        - No sean amigos previamente (ErrorDuplicado).

        Guarda los cambios en el repositorio tras agregarlo.

        Args:
            id_amigo: Id del usuario a agregar como amigo.
        """
        usuario_activo = self._usuario_actual()
        id_activo = usuario_activo.id_usuario

        # Validar que no sea uno mismo
        if id_amigo == id_activo:
            raise ErrorValidacion("No puedes agregarte a ti mismo como amigo.")

        # Validar que el usuario exista
        try:
            self._directorio.obtener_por_id(id_amigo)
        except ErrorNoEncontrado:
            raise ErrorNoEncontrado(
                f"No existe un usuario con el id {id_amigo}."
            )

        # Validar que no sean amigos previamente
        if self._grafo.son_amigos(id_activo, id_amigo):
            raise ErrorDuplicado(
                f"Ya eres amigo del usuario con id {id_amigo}."
            )

        # Agregar la amistad en ambos sentidos
        self._grafo.agregar_amistad(id_activo, id_amigo)
        # Guardar cambios
        self._guardar_amistades()

    def listar_mis_amigos(self) -> list[Usuario]:
        """
        Devuelve la lista de objetos Usuario que son amigos del usuario activo.

        Consulta el directorio para obtener los datos completos de cada amigo.
        """
        usuario_activo = self._usuario_actual()
        ids_amigos = self._grafo.obtener_amigos(usuario_activo.id_usuario)

        amigos: list[Usuario] = []
        for id_amigo in sorted(ids_amigos):
            amigos.append(self._directorio.obtener_por_id(id_amigo))
        return amigos
