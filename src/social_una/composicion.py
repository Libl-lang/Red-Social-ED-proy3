from pathlib import Path

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.almacenamiento.repositorio_usuarios_json import (
    RepositorioUsuariosJson,
)
from social_una.servicios.sesion import Sesion
from social_una.servicios.servicio_autenticacion import (
    ServicioAutenticacion,
)

def crear_servicios():
    """Construye y conecta los componentes principales de M1."""

    # Ubicacion del archivo donde se guardaran los usuarios.
    ruta_datos = Path("datos") / "usuarios.json"

    # Persistencia de datos.
    almacen = AlmacenJson()
    repositorio_usuarios = RepositorioUsuariosJson(
        almacen,
        ruta_datos
    )

    # Control de la sesion.
    sesion = Sesion()

    # Servicio de autenticacion.
    servicio_autenticacion = ServicioAutenticacion(
        repositorio_usuarios,
        sesion
    )

    return {
        "almacen": almacen,
        "repositorio_usuarios": repositorio_usuarios,
        "sesion": sesion,
        "autenticacion": servicio_autenticacion,
    }
