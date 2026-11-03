import unicodedata

from social_una.dominio.modelos import Usuario

class CatalogoUsuarios:
    """Administra los usuarios registrados en memoria."""

    def __init__(self):
        self._usuarios = []
        self._usuarios_por_nombre = {}
        self._usuarios_por_id = {}

    def agregar(self, usuario: Usuario):
        """Agrega un usuario al catalogo."""

        if usuario.id_usuario in self._usuarios_por_id:
            raise ValueError("Ya existe un usuario con ese ID.")

        if usuario.nombre_usuario in self._usuarios_por_nombre:
            raise ValueError("El nombre de usuario ya esta registrado.")

        self._usuarios.append(usuario)
        self._usuarios_por_nombre[usuario.nombre_usuario] = usuario
        self._usuarios_por_id[usuario.id_usuario] = usuario

    def buscar_por_nombre_usuario(self, nombre_usuario: str):
        """Busca un usuario por su nombre de usuario."""
        return self._usuarios_por_nombre.get(nombre_usuario)

    def buscar_por_id(self, id_usuario: int):
        """Busca un usuario por su ID."""
        return self._usuarios_por_id.get(id_usuario)

    def buscar_por_texto(self, texto: str):
        """Busca usuarios por nombre o nombre de usuario."""

        def normalizar(valor):
            valor = valor.lower().strip()

            return "".join(
                caracter
                for caracter in unicodedata.normalize("NFD", valor)
                if unicodedata.category(caracter) != "Mn"
            )

        texto = normalizar(texto)

        resultados = [
            usuario
            for usuario in self._usuarios
            if texto in normalizar(usuario.nombre)
            or texto in normalizar(usuario.nombre_usuario)
        ]

        return sorted(
            resultados,
            key=lambda usuario: normalizar(usuario.nombre)
        )

    def listar_todos(self):
        """Devuelve todos los usuarios registrados."""
        return list(self._usuarios)

    def siguiente_id(self):
        """Calcula el siguiente ID disponible."""

        if not self._usuarios:
            return 1

        return max(self._usuarios_por_id.keys()) + 1
