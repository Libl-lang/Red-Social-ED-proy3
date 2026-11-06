"""
Grafo de amistades no dirigido para Social UNA.

Implementa una lista de adyacencia usando un diccionario donde cada clave es
el id de un usuario (entero) y su valor es un conjunto (set) de ids de amigos.
No hay direccion: si A es amigo de B, entonces B tambien es amigo de A.

Todos los ids se manejan como enteros para evitar problemas de llaves de texto
al cargar desde JSON.
"""


class GrafoAmistades:
    """Grafo no dirigido de amistades usando lista de adyacencia."""

    def __init__(self) -> None:
        """Inicializa el grafo vacio."""
        # Diccionario: id_usuario -> set de ids de amigos
        self._adyacencia: dict[int, set[int]] = {}

    def agregar_amistad(self, id_a: int, id_b: int) -> None:
        """
        Agrega una amistad entre dos usuarios en ambos sentidos.

        Si ya son amigos, no hace nada (idempotente).
        """
        id_a = int(id_a)
        id_b = int(id_b)

        if id_a not in self._adyacencia:
            self._adyacencia[id_a] = set()
        if id_b not in self._adyacencia:
            self._adyacencia[id_b] = set()

        self._adyacencia[id_a].add(id_b)
        self._adyacencia[id_b].add(id_a)

    def obtener_amigos(self, id_usuario: int) -> set[int]:
        """
        Devuelve el conjunto de ids de amigos del usuario dado.

        Si el usuario no existe en el grafo, devuelve un conjunto vacio.
        """
        id_usuario = int(id_usuario)
        return set(self._adyacencia.get(id_usuario, set()))

    def son_amigos(self, id_a: int, id_b: int) -> bool:
        """
        Devuelve True si los dos usuarios son amigos.

        Retorna False si alguno de los dos no existe en el grafo.
        """
        id_a = int(id_a)
        id_b = int(id_b)
        return id_b in self._adyacencia.get(id_a, set())

    def exportar_pares(self) -> list[tuple[int, int]]:
        """
        Exporta todas las amistades como una lista de pares (id_a, id_b).

        Cada amistad se guarda una sola vez con id_a < id_b para evitar
        duplicados en la lista de exportacion.
        """
        pares: list[tuple[int, int]] = []
        vistos: set[tuple[int, int]] = set()

        for id_a, amigos in self._adyacencia.items():
            for id_b in amigos:
                # Ordenar el par para evitar (a,b) y (b,a) duplicados
                par = (min(id_a, id_b), max(id_a, id_b))
                if par not in vistos:
                    vistos.add(par)
                    pares.append(par)

        # Ordenar para salida determinista
        pares.sort()
        return pares

    def cargar_pares(self, pares: list[tuple[int, int]]) -> None:
        """
        Carga amistades desde una lista de pares de ids.

        Convierte todos los elementos a enteros para evitar el error de
        llaves de texto al cargar desde JSON. Reconstruye el grafo desde
        cero con los pares recibidos.
        """
        self._adyacencia = {}
        for par in pares:
            id_a = int(par[0])
            id_b = int(par[1])
            self.agregar_amistad(id_a, id_b)
