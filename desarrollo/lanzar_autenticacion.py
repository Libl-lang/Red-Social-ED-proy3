"""Lanzador aislado del modulo de autenticacion M1."""

import tempfile

from social_una.composicion import construir_aplicacion
from social_una.interfaz.vista_autenticacion import VistaAutenticacion
from social_una.interfaz.ventana_principal import VentanaPrincipal


def ejecutar_autenticacion() -> None:
    """Ejecuta la interfaz con datos temporales de desarrollo."""

    with tempfile.TemporaryDirectory(
        prefix="social_una_autenticacion_"
    ) as temporal:
        app = construir_aplicacion(temporal)
        servicio_autenticacion = app["autenticacion"]

        def abrir_ventana_principal(_usuario) -> None:
            """Abre la ventana principal usando la sesión autenticada."""

            _ = _usuario
            VentanaPrincipal(
                ventana_acceso,
                servicio_autenticacion,
                app["social"],
                app["publicaciones"],
                app["sesion"],
            )

        try:
            ventana_acceso = VistaAutenticacion(
                servicio_autenticacion,
                abrir_ventana_principal,
            )
            ventana_acceso.mainloop()
        finally:
            try:
                if app["sesion"].hay_sesion_iniciada():
                    servicio_autenticacion.cerrar_sesion()
            finally:
                registrador = app["registrador"]
                for manejador in registrador.handlers[:]:
                    registrador.removeHandler(manejador)
                    manejador.close()


if __name__ == "__main__":
    ejecutar_autenticacion()
