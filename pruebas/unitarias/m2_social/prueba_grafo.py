"""
Pruebas unitarias para GrafoAmistades (Modulo 2).

Usa tmp_path para aislar las pruebas y verifica el funcionamiento del
grafo no dirigido de amistades.
"""

from social_una.estructuras.grafo_amistades import GrafoAmistades


def prueba_grafo_vacio_inicialmente():
    """Un grafo recien creado no tiene usuarios ni amistades."""
    grafo = GrafoAmistades()
    assert grafo.obtener_amigos(1) == set()
    assert grafo.son_amigos(1, 2) is False


def prueba_agregar_amistad_ambos_sentidos():
    """Agregar amistad debe insertar en ambos sentidos."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(1, 2)
    assert grafo.son_amigos(1, 2) is True
    assert grafo.son_amigos(2, 1) is True
    assert grafo.obtener_amigos(1) == {2}
    assert grafo.obtener_amigos(2) == {1}


def prueba_agregar_varias_amistades():
    """Se pueden agregar varias amistades sin conflicto."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(1, 2)
    grafo.agregar_amistad(1, 3)
    grafo.agregar_amistad(2, 3)
    assert grafo.obtener_amigos(1) == {2, 3}
    assert grafo.obtener_amigos(2) == {1, 3}
    assert grafo.obtener_amigos(3) == {1, 2}


def prueba_amistad_duplicada_no_causa_error():
    """Agregar la misma amistad dos veces no debe duplicar ni fallar."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(1, 2)
    grafo.agregar_amistad(1, 2)
    grafo.agregar_amistad(2, 1)
    assert grafo.obtener_amigos(1) == {2}
    assert grafo.obtener_amigos(2) == {1}


def prueba_exportar_pares_sin_duplicados():
    """exportar_pares debe devolver cada amistad una sola vez."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(1, 2)
    grafo.agregar_amistad(2, 1)  # misma amistad, otro sentido
    grafo.agregar_amistad(1, 3)
    pares = grafo.exportar_pares()
    assert (1, 2) in pares
    assert (1, 3) in pares
    assert (2, 1) not in pares  # ya esta como (1,2)
    assert len(pares) == 2


def prueba_exportar_pares_ordenados():
    """exportar_pares debe devolver pares ordenados y la lista ordenada."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(3, 1)
    grafo.agregar_amistad(2, 3)
    pares = grafo.exportar_pares()
    assert pares == [(1, 3), (2, 3)]


def prueba_cargar_pares_convierte_a_enteros():
    """cargar_pares debe convertir elementos a enteros (evitar llaves de texto)."""
    grafo = GrafoAmistades()
    # Simular pares como vienen de JSON (podrían ser strings)
    grafo.cargar_pares([("1", "2"), ("2", "3")])
    assert grafo.son_amigos(1, 2) is True
    assert grafo.son_amigos(2, 3) is True
    assert grafo.son_amigos(1, 3) is False


def prueba_cargar_pares_reconstruye_grafo():
    """cargar_pares reconstruye el grafo desde cero."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(1, 2)
    grafo.cargar_pares([(3, 4)])
    assert grafo.son_amigos(1, 2) is False  # se borraron las previas
    assert grafo.son_amigos(3, 4) is True


def prueba_obtener_amigos_usuario_sin_amigos():
    """Un usuario sin amistades devuelve conjunto vacio."""
    grafo = GrafoAmistades()
    grafo.agregar_amistad(1, 2)
    assert grafo.obtener_amigos(99) == set()


def prueba_son_amigos_usuario_inexistente_retorna_falso():
    """son_amigos con usuarios no registrados retorna False."""
    grafo = GrafoAmistades()
    assert grafo.son_amigos(99, 100) is False