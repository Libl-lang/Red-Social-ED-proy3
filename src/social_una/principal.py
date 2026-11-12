from social_una.composicion import construir_aplicacion
from social_una.interfaz.vista_autenticacion import VistaAutenticacion
from social_una.interfaz.ventana_principal import VentanaPrincipal


def ejecutar_aplicacion():
    """Inicia la aplicacion Social UNA."""

    # Construir los servicios reales de M1, M2 y M3.
    app = construir_aplicacion("datos")

    servicio_autenticacion = app["autenticacion"]
    servicio_social = app["social"]
    servicio_publicaciones = app["publicaciones"]
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
