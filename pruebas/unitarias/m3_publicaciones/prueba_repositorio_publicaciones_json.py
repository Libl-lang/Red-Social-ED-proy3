"""
Pruebas unitarias de RepositorioPublicacionesJson.

Comprueban que el repositorio guarda y carga publicaciones en un archivo JSON,
y que reacciona bien cuando el archivo falta o tiene problemas. Usan la
carpeta temporal tmp_path de pytest, que se crea nueva para cada prueba y se
limpia sola, así que nunca tocan los datos reales del proyecto.
"""

import json

import pytest

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.almacenamiento.repositorio_publicaciones_json import (
    RepositorioPublicacionesJson,
)
from social_una.dominio.contratos import RepositorioPublicaciones
from social_una.dominio.errores import ErrorAlmacenamiento
from social_una.dominio.modelos import Publicacion


@pytest.fixture
def ruta(tmp_path):
    """Ruta del archivo publicaciones.json dentro de la carpeta temporal de la prueba."""
    # El archivo todavía no existe: cada prueba decide si lo crea
    return tmp_path / "publicaciones.json"


@pytest.fixture
def repositorio(ruta):
    """Repositorio listo para usar, apuntando al archivo temporal."""
    return RepositorioPublicacionesJson(ruta, AlmacenJson())


def crear_publicaciones_de_ejemplo() -> list[Publicacion]:
    """Devuelve dos publicaciones de ejemplo."""
    return [
        Publicacion(1, 2, "Hola mundo", "2026-11-03T09:00:00+00:00"),
        Publicacion(2, 1, "Segundo mensaje", "2026-11-03T10:00:00+00:00"),
    ]


def prueba_el_repositorio_cumple_el_contrato(repositorio):
    """El repositorio hereda del contrato RepositorioPublicaciones de la Fase 0."""
    # Si cumple el contrato, otros módulos pueden recibirlo en lugar de la pieza falsa
    assert isinstance(repositorio, RepositorioPublicaciones)


def prueba_cargar_sin_archivo_devuelve_lista_vacia(repositorio, ruta):
    """Si publicaciones.json no existe todavía, se carga una lista vacía y no un error."""
    # Preparar: no se crea ningún archivo
    assert not ruta.exists()
    # Ejecutar y comprobar: la app puede arrancar vacía la primera vez
    assert repositorio.cargar_todo() == []


def prueba_guardar_y_cargar_devuelve_las_mismas_publicaciones(repositorio):
    """Lo que se guarda vuelve igual al cargar."""
    publicaciones = crear_publicaciones_de_ejemplo()
    # Ejecutar: se guardan las dos publicaciones y se cargan de nuevo
    repositorio.guardar_todo(publicaciones)
    cargadas = repositorio.cargar_todo()
    # Comprobar: ids, autores, textos y fechas son idénticos
    assert cargadas == publicaciones


def prueba_guardar_escribe_una_lista_de_diccionarios_en_json(repositorio, ruta):
    """El archivo guardado es una lista JSON con una publicación por elemento."""
    publicaciones = crear_publicaciones_de_ejemplo()
    repositorio.guardar_todo(publicaciones)
    # Se lee el archivo directamente, sin usar el repositorio, para ver su contenido real
    contenido = json.loads(ruta.read_text(encoding="utf-8"))
    assert contenido == [p.a_diccionario() for p in publicaciones]


def prueba_guardar_reemplaza_lo_anterior(repositorio):
    """Cada guardado reemplaza todo el contenido, no agrega al final."""
    publicaciones = crear_publicaciones_de_ejemplo()
    repositorio.guardar_todo(publicaciones)
    # Ejecutar: se guarda una lista con una sola publicación
    repositorio.guardar_todo([publicaciones[0]])
    # Comprobar: queda solo esa, la segunda ya no está
    assert repositorio.cargar_todo() == [publicaciones[0]]


def prueba_guardar_lista_vacia_crea_un_archivo_que_se_carga_vacio(repositorio, ruta):
    """Guardar una lista vacía deja un archivo válido que se carga como lista vacía."""
    repositorio.guardar_todo([])
    # El archivo existe (es una lista vacía) y se puede volver a leer sin error
    assert ruta.exists()
    assert repositorio.cargar_todo() == []


def prueba_guardar_crea_las_carpetas_que_falten(tmp_path):
    """Si la carpeta del archivo no existe, se crea al guardar."""
    # Preparar: una ruta dentro de dos carpetas que todavía no existen
    ruta_anidada = tmp_path / "datos" / "ejecucion" / "publicaciones.json"
    repositorio = RepositorioPublicacionesJson(ruta_anidada, AlmacenJson())
    # Ejecutar: al guardar se crean las carpetas y el archivo
    repositorio.guardar_todo(crear_publicaciones_de_ejemplo())
    assert ruta_anidada.exists()


def prueba_guardar_no_deja_archivos_temporales(repositorio, tmp_path):
    """La escritura segura no deja el archivo .tmp cuando termina bien."""
    repositorio.guardar_todo(crear_publicaciones_de_ejemplo())
    # No debe quedar ningún archivo con extensión .tmp en la carpeta
    assert list(tmp_path.glob("*.tmp")) == []


def prueba_se_conservan_tildes_y_enie(repositorio):
    """Los textos con tildes, eñes y signos de pregunta se guardan y cargan sin dañarse."""
    publicacion = Publicacion(
        1, 1, "¿Qué tal, compañeros? Mañana hay clase de verano", "2026-11-03T09:00:00+00:00"
    )
    repositorio.guardar_todo([publicacion])
    # Comprobar: el texto es idéntico después de ir al archivo y volver
    assert repositorio.cargar_todo() == [publicacion]


def prueba_ids_guardados_como_texto_vuelven_como_enteros(repositorio, ruta):
    """Si el archivo trae los ids como texto, al cargar se convierten en enteros."""
    # Preparar: un archivo escrito a mano con los ids entre comillas
    ruta.write_text(
        '[{"id_publicacion": "7", "id_autor": "2", "texto": "x", "fecha_creacion": "f"}]',
        encoding="utf-8",
    )
    publicacion = repositorio.cargar_todo()[0]
    # Comprobar: los ids son números, no texto (decisión 1 de la Fase 0)
    assert publicacion.id_publicacion == 7
    assert publicacion.id_autor == 2


def prueba_archivo_corrupto_lanza_error_de_almacenamiento(repositorio, ruta):
    """Un archivo que no es JSON válido lanza ErrorAlmacenamiento."""
    ruta.write_text("{ roto", encoding="utf-8")
    # El mensaje viene de AlmacenJson y dice que el archivo está dañado
    with pytest.raises(ErrorAlmacenamiento, match="dañado"):
        repositorio.cargar_todo()


def prueba_archivo_vacio_lanza_error_de_almacenamiento(repositorio, ruta):
    """Un archivo de 0 bytes se considera dañado."""
    ruta.write_text("", encoding="utf-8")
    with pytest.raises(ErrorAlmacenamiento, match="dañado"):
        repositorio.cargar_todo()


def prueba_contenido_que_no_es_una_lista_lanza_error(repositorio, ruta):
    """Un JSON válido que no es una lista de publicaciones lanza ErrorAlmacenamiento."""
    # Preparar: un objeto JSON válido, pero no una lista
    ruta.write_text('{"a": 1}', encoding="utf-8")
    with pytest.raises(ErrorAlmacenamiento, match="formato esperado"):
        repositorio.cargar_todo()


def prueba_publicacion_incompleta_lanza_error(repositorio, ruta):
    """Una publicación a la que le faltan campos lanza ErrorAlmacenamiento."""
    # Preparar: solo trae el id; faltan autor, texto y fecha
    ruta.write_text('[{"id_publicacion": 1}]', encoding="utf-8")
    with pytest.raises(ErrorAlmacenamiento, match="incompletas"):
        repositorio.cargar_todo()


def prueba_dato_invalido_lanza_error(repositorio, ruta):
    """Un id que no es un número lanza ErrorAlmacenamiento."""
    # Preparar: "abc" no se puede convertir a entero
    ruta.write_text(
        '[{"id_publicacion": "abc", "id_autor": 1, "texto": "x", "fecha_creacion": "f"}]',
        encoding="utf-8",
    )
    with pytest.raises(ErrorAlmacenamiento, match="inválidos"):
        repositorio.cargar_todo()