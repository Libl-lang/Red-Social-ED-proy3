"""
Historial de publicaciones en memoria.
----------------------------------------------------------------------------
Este archivo define la estructura de datos que guarda las publicaciones de la
red social en una lista dinámica. No sabe de archivos ni de pantallas.
"""

from social_una.dominio.modelos import Publicacion


class HistorialPublicaciones:
    """
    Guarda las publicaciones en el orden en que se agregan.
    La más antigua queda al principio de la lista y la más reciente al final.
    Quien arma el muro (ServicioPublicaciones) es quien lo ordena de la más
    reciente a la más antigua.
    """

    def __init__(self, publicaciones_iniciales: list[Publicacion] | None = None) -> None:
        
        """Crea el historial, vacío o con una copia de las publicaciones recibidas."""
        # Se guarda una copia para no modificar la lista original de quien llama
        if publicaciones_iniciales is not None:
            self._publicaciones = list(publicaciones_iniciales)
        else:
            self._publicaciones = []

    def agregar(self, publicacion: Publicacion) -> None:
        """Agrega una publicación al final del historial."""
        # append mantiene el orden de inserción: la nueva queda de última
        self._publicaciones.append(publicacion)

    def obtener_por_autor(self, id_autor: int) -> list[Publicacion]:
        """Devuelve las publicaciones de un solo autor, en el orden guardado."""
        # Recorre cada publicación y conserva solo las del autor pedido
        return [p for p in self._publicaciones if p.id_autor == id_autor]

    def obtener_de_autores(self, ids_autores: set[int]) -> list[Publicacion]:
        """Devuelve las publicaciones de varios autores, en el orden guardado."""
        # Igual que el anterior, pero acepta cualquier autor que esté en el conjunto
        return [p for p in self._publicaciones if p.id_autor in ids_autores]

    def listar_todas(self) -> list[Publicacion]:
        """Devuelve una copia de todas las publicaciones."""
        # Se entrega una copia para que quien llama no pueda alterar el historial
        return list(self._publicaciones)

    def siguiente_id(self) -> int:
        """Devuelve el id que le corresponde a la próxima publicación."""
        # Si no hay publicaciones, el primer id es 1
        if not self._publicaciones:
            return 1
        # Se usa el id más alto + 1 (y no la cantidad) para no repetir ids si faltan números
        return max(p.id_publicacion for p in self._publicaciones) + 1