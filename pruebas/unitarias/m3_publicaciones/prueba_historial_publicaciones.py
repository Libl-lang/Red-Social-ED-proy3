"""
Pruebas unitarias de HistorialPublicaciones.

Comprueban que la estructura agrega, filtra y numera las publicaciones como
se espera. Usan una tabla fija: las publicaciones 1 (autor 2), 2 (autor 3),
3 (autor 2) y 4 (autor 1), agregadas en ese orden.

Cada prueba sigue tres pasos: preparar los datos, ejecutar el método que se
quiere probar y comprobar el resultado con assert. Si algún assert no se
cumple, pytest marca la prueba en rojo y muestra qué esperaba y qué obtuvo.
"""

from social_una.dominio.modelos import Publicacion
from social_una.estructuras.historial_publicaciones import HistorialPublicaciones


def crear_publicacion(id_publicacion: int, id_autor: int) -> Publicacion:
    """Crea una publicación de ejemplo; en estas pruebas solo importan el id y el autor."""
    # El texto y la fecha son siempre los mismos porque el historial no los usa
    return Publicacion(
        id_publicacion, id_autor, "texto de prueba", "2026-11-03T09:00:00+00:00"
    )


def crear_historial_de_ejemplo() -> HistorialPublicaciones:
    """Devuelve un historial con la tabla fija de cuatro publicaciones."""
    historial = HistorialPublicaciones()
    # Cada pareja es (id de la publicación, id del autor), en el orden en que se agregan
    for id_publicacion, id_autor in ((1, 2), (2, 3), (3, 2), (4, 1)):
        historial.agregar(crear_publicacion(id_publicacion, id_autor))
    return historial


def ids(publicaciones: list[Publicacion]) -> list[int]:
    """Devuelve solo los ids de una lista de publicaciones, para comparar fácil."""
    # Comparar [1, 3] es más sencillo que comparar objetos Publicacion completos
    return [p.id_publicacion for p in publicaciones]


def prueba_historial_nuevo_esta_vacio():
    """Un historial recién creado no tiene publicaciones y su primer id es 1."""
    # Preparar: un historial sin ninguna publicación
    historial = HistorialPublicaciones()
    # Comprobar: la lista está vacía y el primer id disponible es 1
    assert historial.listar_todas() == []
    assert historial.siguiente_id() == 1


def prueba_agregar_mantiene_el_orden_de_insercion():
    """Las publicaciones quedan en el orden en que se agregaron, no ordenadas por otro criterio."""
    # Preparar: se agregan las publicaciones 1, 2, 3 y 4, en ese orden
    historial = crear_historial_de_ejemplo()
    # Comprobar: la lista las devuelve en el mismo orden de llegada
    assert ids(historial.listar_todas()) == [1, 2, 3, 4]


def prueba_obtener_por_autor_devuelve_solo_las_de_ese_autor():
    """Al pedir las de un autor, solo salen las suyas."""
    historial = crear_historial_de_ejemplo()
    # Ejecutar: se piden las del autor 2 (Beto), que escribió la 1 y la 3
    resultado = historial.obtener_por_autor(2)
    # Comprobar: la 2 (autor 3) y la 4 (autor 1) no aparecen
    assert ids(resultado) == [1, 3]


def prueba_obtener_por_autor_sin_publicaciones_devuelve_lista_vacia():
    """Si el autor no tiene publicaciones, se devuelve una lista vacía y no un error."""
    historial = crear_historial_de_ejemplo()
    # Ejecutar: el autor 99 no existe en la tabla
    resultado = historial.obtener_por_autor(99)
    # Comprobar: la respuesta es una lista vacía
    assert resultado == []


def prueba_obtener_de_autores_devuelve_las_de_varios_autores_en_orden_guardado():
    """Con varios autores a la vez salen las de todos, en el orden en que se guardaron."""
    historial = crear_historial_de_ejemplo()
    # Ejecutar: se piden las de los autores 1 y 2 (Ana y Beto)
    resultado = historial.obtener_de_autores({1, 2})
    # Comprobar: salen la 1, la 3 y la 4; la 2 (autor 3) queda fuera.
    # No vienen ordenadas de la más reciente: ese orden lo da el servicio
    assert ids(resultado) == [1, 3, 4]


def prueba_obtener_de_autores_con_conjunto_vacio_devuelve_lista_vacia():
    """Si no se pide ningún autor, no se devuelve ninguna publicación."""
    historial = crear_historial_de_ejemplo()
    # Ejecutar: un conjunto vacío no contiene a ningún autor
    resultado = historial.obtener_de_autores(set())
    # Comprobar: no coincide ninguna publicación
    assert resultado == []


def prueba_siguiente_id_es_el_mas_alto_mas_uno():
    """El id siguiente es el más alto que existe más uno, aunque falten números."""
    # Caso 1: con los ids 1, 2, 3 y 4 el más alto es 4, así que el siguiente es 5
    assert crear_historial_de_ejemplo().siguiente_id() == 5
    # Caso 2: con los ids 1, 2 y 7 faltan el 3, 4, 5 y 6. Si se contara la cantidad
    # (3 publicaciones) el siguiente sería 4; con el más alto (7) es 8
    historial = HistorialPublicaciones(
        [crear_publicacion(1, 1), crear_publicacion(2, 1), crear_publicacion(7, 1)]
    )
    assert historial.siguiente_id() == 8


def prueba_listar_todas_devuelve_una_copia():
    """Quien recibe la lista no puede alterar el historial por accidente."""
    historial = crear_historial_de_ejemplo()
    # Ejecutar: se pide la lista y se vacía por completo
    copia = historial.listar_todas()
    copia.clear()
    # Comprobar: el historial sigue con sus 4 publicaciones, porque se vació una copia
    assert len(historial.listar_todas()) == 4


def prueba_el_constructor_guarda_una_copia_de_la_lista_inicial():
    """Cambiar la lista con la que se creó el historial no modifica el historial."""
    # Preparar: una lista con una publicación, entregada al constructor
    lista_original = [crear_publicacion(1, 1)]
    historial = HistorialPublicaciones(lista_original)
    # Ejecutar: se agrega otra publicación a la lista original, no al historial
    lista_original.append(crear_publicacion(2, 1))
    # Comprobar: el historial sigue con una sola publicación
    assert len(historial.listar_todas()) == 1


def prueba_un_historial_cargado_continua_los_ids():
    """Un historial reconstruido con datos guardados sigue numerando desde donde quedó."""
    historial = crear_historial_de_ejemplo()
    # Ejecutar: se crea un historial nuevo con las publicaciones del anterior,
    # como pasa al abrir la app y leer publicaciones.json
    reconstruido = HistorialPublicaciones(historial.listar_todas())
    # Comprobar: el siguiente id es 5, igual que en el original
    assert reconstruido.siguiente_id() == 5