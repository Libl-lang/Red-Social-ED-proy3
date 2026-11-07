import unicodedata

from social_una.dominio.errores import ErrorDuplicado
from social_una.dominio.modelos import Usuario

class CatalogoUsuarios:
    """Administra los usuarios registrados en memoria."""

    def __init__(self):
        self._usuarios = []
        self._usuarios_por_nombre = {}
        self._usuarios_por_id = {}

    @staticmethod
    def _normalizar(texto: str) -> str:
        """Normaliza un texto para comparar sin distinguir tildes."""

        texto = texto.lower().strip()

        return "".join(
            caracter
            for caracter in unicodedata.normalize("NFD", texto)
            if unicodedata.category(caracter) != "Mn"
        )

    def agregar(self, usuario: Usuario):
        """Agrega un usuario al catalogo."""

        nombre_normalizado = self._normalizar(
            usuario.nombre_usuario
        )

        if usuario.id_usuario in self._usuarios_por_id:
            raise ErrorDuplicado(
                "Ya existe un usuario con ese ID."
            )

        if nombre_normalizado in self._usuarios_por_nombre:
            raise ErrorDuplicado(
                "El nombre de usuario ya esta registrado."
            )

        self._usuarios.append(usuario)

        self._usuarios_por_nombre[nombre_normalizado] = usuario
        self._usuarios_por_id[usuario.id_usuario] = usuario

    def buscar_por_nombre_usuario(self, nombre_usuario: str):
        """Busca un usuario sin distinguir mayusculas ni tildes."""

        nombre_normalizado = self._normalizar(nombre_usuario)

        return self._usuarios_por_nombre.get(nombre_normalizado)

    def buscar_por_id(self, id_usuario: int):
        """Busca un usuario por su ID."""

        return self._usuarios_por_id.get(id_usuario)

    def buscar_por_texto(self, texto: str):
        """Busca usuarios por nombre o nombre de usuario."""

        texto_normalizado = self._normalizar(texto)

        resultados = [
            usuario
            for usuario in self._usuarios
            if texto_normalizado in self._normalizar(usuario.nombre)
            or texto_normalizado in self._normalizar(
                usuario.nombre_usuario
            )
        ]

        return sorted(
            resultados,
            key=lambda usuario: self._normalizar(usuario.nombre)
        )

    def listar_todos(self):
        """Devuelve todos los usuarios registrados."""

        return list(self._usuarios)

    def siguiente_id(self):
        """Calcula el siguiente ID disponible."""

        if not self._usuarios:
            return 1

        return max(self._usuarios_por_id.keys()) + 1
