"""
Composición de la aplicación Social UNA (Fase 2 - Integración).

Construye y conecta todos los componentes reales de la aplicación:
almacenamiento, repositorios, servicios e interfaz, siguiendo el orden
estricto de inyección de dependencias.
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
from social_una.servicios.servicio_autenticacion import (
    ServicioAutenticacion,
)
from social_una.servicios.servicio_social import ServicioSocial
from social_una.servicios.servicio_publicaciones import ServicioPublicaciones
from social_una.interfaz.ventana_principal import VentanaPrincipal


def _configurar_persistencia_inicial(
    ruta_ejecucion: Path, ruta_semilla: Path
) -> None:
    """
    Configura la persistencia inicial.

    Crea la carpeta de ejecución si no existe y copia los archivos de semilla
    (por ejemplo amistades.json) a la carpeta de ejecución solo cuando aún no
    existen allí. Nunca sobrescribe archivos ya creados por la aplicación, así
    los datos del usuario (usuarios, publicaciones y amistades nuevas) se
    conservan entre reinicios.
    """
    ruta_ejecucion.mkdir(parents=True, exist_ok=True)

    if not ruta_semilla.exists():
        return

    for archivo_semilla in ruta_semilla.iterdir():
        if not archivo_semilla.is_file():
            continue
        destino = ruta_ejecucion / archivo_semilla.name
        if not destino.exists():
            shutil.copy2(archivo_semilla, destino)


def construir_aplicacion(ruta_datos: str | Path, ventana_padre=None) -> dict:
    """
    Construye y conecta todos los componentes principales de Social UNA.

    Sigue este orden estricto:

    1. Configurar la persistencia inicial (copiar semilla a ejecución si es necesario).
    2. Instanciar AlmacenJson y los tres repositorios reales.
    3. Crear la Sesion y el ServicioAutenticacion (cumple DirectorioUsuarios).
    4. Crear el ServicioSocial inyectándole su repositorio, el servicio de
       autenticación y la sesión (cumple ConsultaAmistades).
    5. Crear el ServicioPublicaciones inyectándole su repositorio, el servicio
       social, el servicio de autenticación y la sesión.
    6. Instanciar la VentanaPrincipal pasándole los tres servicios reales y
       la sesión.

    Args:
        ruta_datos: Carpeta donde se guardan los archivos de datos de ejecución.
        ventana_padre: Ventana padre de Tkinter (opcional).

    Returns:
        Diccionario con todos los componentes construidos.
    """
    ruta_datos = Path(ruta_datos)
    ruta_semilla = Path("datos") / "semilla"

    # ------------------------------------------------------------------
    # 1. Persistencia inicial: copiar datos de semilla a ejecución si es necesario.
    # ------------------------------------------------------------------
    _configurar_persistencia_inicial(ruta_datos, ruta_semilla)

    # ------------------------------------------------------------------
    # 2. Almacenamiento y los tres repositorios reales.
    # ------------------------------------------------------------------
    almacen = AlmacenJson()

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

    # ------------------------------------------------------------------
    # 3. Sesión y ServicioAutenticacion (implementa DirectorioUsuarios).
    # ------------------------------------------------------------------
    sesion = Sesion()
    servicio_autenticacion = ServicioAutenticacion(
        repositorio_usuarios,
        sesion,
    )

    # ------------------------------------------------------------------
    # 4. ServicioSocial (implementa ConsultaAmistades).
    #    Se inyecta: repositorio de amistades, servicio de autenticación,
    #    y sesión.
    # ------------------------------------------------------------------
    servicio_social = ServicioSocial(
        repositorio_amistades,
        servicio_autenticacion,
        sesion,
    )

    # ------------------------------------------------------------------
    # 5. ServicioPublicaciones.
    #    Se inyecta: repositorio de publicaciones, servicio social,
    #    servicio de autenticación, y sesión.
    # ------------------------------------------------------------------
    servicio_publicaciones = ServicioPublicaciones(
        repositorio_publicaciones,
        servicio_social,
        servicio_autenticacion,
        sesion,
    )

    # ------------------------------------------------------------------
    # 6. VentanaPrincipal con los tres servicios y la sesión.
    # ------------------------------------------------------------------
    ventana = VentanaPrincipal(
        ventana_padre,
        servicio_autenticacion,
        servicio_social,
        servicio_publicaciones,
        sesion,
    )

    return {
        "almacen": almacen,
        "repositorio_usuarios": repositorio_usuarios,
        "repositorio_amistades": repositorio_amistades,
        "repositorio_publicaciones": repositorio_publicaciones,
        "sesion": sesion,
        "autenticacion": servicio_autenticacion,
        "social": servicio_social,
        "publicaciones": servicio_publicaciones,
        "ventana": ventana,
    }
