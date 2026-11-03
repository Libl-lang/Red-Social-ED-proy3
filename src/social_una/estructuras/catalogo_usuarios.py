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
        texto = texto.lower().strip()

        return [
            usuario
            for usuario in self._usuarios
            if texto in usuario.nombre.lower()
            or texto in usuario.nombre_usuario.lower()
        ]

    def listar_todos(self):
        """Devuelve todos los usuarios registrados."""
        return list(self._usuarios)

    def siguiente_id(self):
        """Calcula el siguiente ID disponible."""
        if not self._usuarios:
            return 1

        return max(self._usuarios_por_id.keys()) + 1
