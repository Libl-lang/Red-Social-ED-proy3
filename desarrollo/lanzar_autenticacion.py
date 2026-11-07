"""Lanzador independiente del modulo de autenticacion M1."""

from social_una.composicion import crear_servicios
from social_una.interfaz.vista_autenticacion import VistaAutenticacion
from social_una.interfaz.ventana_principal import VentanaPrincipal

def ejecutar_autenticacion():
    """Ejecuta el modulo de autenticacion de Social UNA."""

    servicios = crear_servicios()
    servicio_autenticacion = servicios["autenticacion"]

    ventana_acceso = None
    ventana_principal = None

    def abrir_ventana_principal(usuario):
        """Abre la ventana principal despues del inicio de sesion."""
        nonlocal ventana_principal

        ventana_principal = VentanaPrincipal(
            ventana_acceso,
            usuario,
            servicio_autenticacion,
            volver_al_login
        )

    def volver_al_login():
        """Regresa a la pantalla de inicio de sesion."""
        ventana_acceso.deiconify()
        ventana_acceso.mostrar_login()

    ventana_acceso = VistaAutenticacion(
        servicio_autenticacion,
        abrir_ventana_principal
    )

    ventana_acceso.mainloop()


if __name__ == "__main__":
    ejecutar_autenticacion()
