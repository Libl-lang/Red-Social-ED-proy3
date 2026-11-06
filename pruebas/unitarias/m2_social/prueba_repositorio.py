"""
Pruebas unitarias para RepositorioAmistadesJson (Modulo 2).

Usa tmp_path para aislar las pruebas y verifica la lectura y escritura
de amistades en archivo JSON usando AlmacenJson.
"""

import json

from social_una.almacenamiento.repositorio_amistades_json import RepositorioAmistadesJson


def prueba_cargar_todo_archivo_inexistente_devuelve_lista_vacia(tmp_path):
    """Si el archivo no existe, cargar_todo devuelve lista vacia."""
    ruta = tmp_path / "amistades.json"
    repo = RepositorioAmistadesJson(ruta)
    pares = repo.cargar_todo()
    assert pares == []


def prueba_guardar_y_cargar_todo(tmp_path):
    """Guardar y cargar debe conservar los pares de amistad."""
    ruta = tmp_path / "amistades.json"
    repo = RepositorioAmistadesJson(ruta)

    pares_originales = [(1, 2), (2, 3), (1, 3)]
    repo.guardar_todo(pares_originales)

    pares_cargados = repo.cargar_todo()
    assert pares_cargados == [(1, 2), (1, 3), (2, 3)]  # ordenados


def prueba_guardar_todo_reemplaza_contenido_anterior(tmp_path):
    """guardar_todo reemplaza completamente el contenido anterior."""
    ruta = tmp_path / "amistades.json"
    repo = RepositorioAmistadesJson(ruta)

    repo.guardar_todo([(1, 2)])
    repo.guardar_todo([(3, 4), (5, 6)])

    pares = repo.cargar_todo()
    assert pares == [(3, 4), (5, 6)]


def prueba_ids_se_guardan_como_enteros(tmp_path):
    """Los ids se guardan como enteros en el archivo JSON."""
    ruta = tmp_path / "amistades.json"
    repo = RepositorioAmistadesJson(ruta)

    repo.guardar_todo([(1, 2)])

    # Leer el archivo crudo para verificar que son enteros
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    assert datos == [[1, 2]]
    assert isinstance(datos[0][0], int)
    assert isinstance(datos[0][1], int)


def prueba_cargar_todo_convierte_a_enteros(tmp_path):
    """cargar_todo convierte elementos a enteros aunque venga de JSON como texto."""
    ruta = tmp_path / "amistades.json"
    # Escribir manualmente con strings para simular JSON con llaves de texto
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump([["1", "2"], ["2", "3"]], f)

    repo = RepositorioAmistadesJson(ruta)
    pares = repo.cargar_todo()

    assert pares == [(1, 2), (2, 3)]
    assert isinstance(pares[0][0], int)
    assert isinstance(pares[0][1], int)