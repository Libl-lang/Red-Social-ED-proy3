from pathlib import Path

from social_una.composicion import construir_aplicacion
from social_una.interfaz.vista_autenticacion import VistaAutenticacion
from social_una.interfaz.ventana_principal import VentanaPrincipal

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_DATOS = RAIZ_PROYECTO / "datos"


def ejecutar_aplicacion():
    """Inicia la aplicacion Social UNA."""

    # Construir los servicios reales de M1, M2 y M3.
    app = construir_aplicacion(RUTA_DATOS)

    servicio_autenticacion = app["autenticacion"]
    servicio_social = app["social"]
    servicio_publicaciones = app["publicaciones"]
    servicio_cuenta = app["cuenta"]
    sesion = app["sesion"]

    ventana_acceso = None

    def abrir_ventana_principal(usuario):
        """Abre la ventana principal después de iniciar sesión."""

        VentanaPrincipal(
            ventana_acceso,
            servicio_autenticacion,
            servicio_social,
            servicio_publicaciones,
            sesion,
            servicio_cuenta,
        )

    # Crear la ventana de autenticación.
    ventana_acceso = VistaAutenticacion(
        servicio_autenticacion,
        abrir_ventana_principal,
    )

    # Mantener activa la aplicación.
    ventana_acceso.mainloop()


if __name__ == "__main__":
    ejecutar_aplicacion()
