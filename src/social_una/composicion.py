"""
Composición de la aplicación Social UNA.

Construye y conecta los componentes de almacenamiento,
repositorios, sesión, servicios y registro de eventos.
"""

from pathlib import Path
import shutil

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.almacenamiento.repositorio_usuarios_json import (
    RepositorioUsuariosJson,
)
from social_una.almacenamiento.repositorio_amistades_json import (
    RepositorioAmistadesJson,
)
from social_una.almacenamiento.repositorio_publicaciones_json import (
    RepositorioPublicacionesJson,
)
from social_una.servicios.sesion import Sesion
from social_una.servicios.registro_eventos import crear_registrador
from social_una.servicios.servicio_autenticacion import (
    ServicioAutenticacion,
)
from social_una.servicios.servicio_social import ServicioSocial
from social_una.servicios.servicio_publicaciones import (
    ServicioPublicaciones,
)


def _configurar_persistencia_inicial(
    ruta_ejecucion: Path, ruta_semilla: Path
) -> None:
    """Copia los archivos iniciales sin sobrescribir datos existentes."""

    ruta_ejecucion.mkdir(parents=True, exist_ok=True)

    if not ruta_semilla.exists():
        return

    for archivo_semilla in ruta_semilla.iterdir():
        if not archivo_semilla.is_file():
            continue

        destino = ruta_ejecucion / archivo_semilla.name

        if not destino.exists():
            shutil.copy2(archivo_semilla, destino)


def construir_aplicacion(ruta_datos: str | Path) -> dict:
    """
    Construye y conecta los componentes de Social UNA.

    La interfaz gráfica se construye por separado en principal.py.
    """

    ruta_datos = Path(ruta_datos)
    ruta_semilla = Path("datos") / "semilla"

    # 1. Configurar persistencia inicial.
    _configurar_persistencia_inicial(ruta_datos, ruta_semilla)

    # 2. Crear almacenamiento, repositorios y registrador.
    almacen = AlmacenJson()
    registrador = crear_registrador(ruta_datos)

    repositorio_usuarios = RepositorioUsuariosJson(
        almacen,
        ruta_datos / "usuarios.json",
    )

    repositorio_amistades = RepositorioAmistadesJson(
        ruta_datos / "amistades.json",
    )

    repositorio_publicaciones = RepositorioPublicacionesJson(
        ruta_datos / "publicaciones.json",
        almacen,
    )

    # 3. Crear sesión y autenticación.
    sesion = Sesion()

    servicio_autenticacion = ServicioAutenticacion(
        repositorio_usuarios,
        sesion,
        registrador=registrador,
    )

    # 4. Crear servicio social.
    servicio_social = ServicioSocial(
        repositorio_amistades,
        servicio_autenticacion,
        sesion,
        registrador=registrador,
    )

    # 5. Crear servicio de publicaciones.
    servicio_publicaciones = ServicioPublicaciones(
        repositorio_publicaciones,
        servicio_social,
        servicio_autenticacion,
        sesion,
        registrador=registrador,
    )

    # 6. Devolver componentes.
    return {
        "almacen": almacen,
        "repositorio_usuarios": repositorio_usuarios,
        "repositorio_amistades": repositorio_amistades,
        "repositorio_publicaciones": repositorio_publicaciones,
        "sesion": sesion,
        "registrador": registrador,
        "autenticacion": servicio_autenticacion,
        "social": servicio_social,
        "publicaciones": servicio_publicaciones,
    }
