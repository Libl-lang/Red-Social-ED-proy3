from social_una.composicion import construir_aplicacion
from social_una.interfaz.vista_autenticacion import VistaAutenticacion

def ejecutar_aplicacion():
    """Inicia la aplicacion Social UNA."""

    # Construir todos los componentes reales (M1 + M2 + M3) y la interfaz.
    # ruta_datos es la carpeta de ejecucion donde se guardan los archivos.
    app = construir_aplicacion("datos")

    servicio_autenticacion = app["autenticacion"]
    servicio_social = app["social"]
    servicio_publicaciones = app["publicaciones"]
    sesion = app["sesion"]

    ventana_acceso = None
    ventana_principal = None

    def abrir_ventana_principal(usuario):
        """Abre la ventana principal despues del inicio de sesion.

        Inicia la sesion del usuario y crea la VentanaPrincipal con los
        tres servicios reales y la sesion.
        """
        nonlocal ventana_principal

        # Iniciar sesion del usuario autenticado
        sesion.iniciar(usuario)

        ventana_principal = VentanaPrincipal(
            ventana_acceso,
            servicio_autenticacion,
            servicio_social,
            servicio_publicaciones,
            sesion,
        )
        ventana_acceso.withdraw()

    def volver_al_login():
        """Regresa a la pantalla de inicio de sesion."""
        ventana_acceso.deiconify()
        ventana_acceso.mostrar_login()

    # Crear la ventana de autenticacion.
    ventana_acceso = VistaAutenticacion(
        servicio_autenticacion,
        abrir_ventana_principal,
    )

    # Mantener activa la aplicacion.
    ventana_acceso.mainloop()


if __name__ == "__main__":
    ejecutar_aplicacion()
