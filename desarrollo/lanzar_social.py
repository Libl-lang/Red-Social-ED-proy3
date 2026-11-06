"""
Lanzador aislado de la vista social de Social UNA.

Permite probar la vista de forma aislada usando las piezas falsas:
DirectorioUsuariosFalso, SesionFalsa y RepositorioAmistadesJson.
"""

import tkinter as tk

from social_una.almacenamiento.repositorio_amistades_json import RepositorioAmistadesJson
from social_una.interfaz.vista_social import VistaSocial
from social_una.servicios.servicio_social import ServicioSocial
from pruebas.falsos.directorio_usuarios_falso import DirectorioUsuariosFalso, USUARIOS_FALSOS
from pruebas.falsos.sesion_falsa import SesionFalsa


def main() -> None:
    """Inicia la aplicacion social con componentes falsos para pruebas."""
    root = tk.Tk()

    # Crear piezas falsas para prueba aislada
    directorio = DirectorioUsuariosFalso()
    sesion = SesionFalsa(usuario_inicial=USUARIOS_FALSOS[0])  # Ana Mora

    # Repositorio en una ruta temporal para pruebas
    repo = RepositorioAmistadesJson("datos/semilla/amistades.json")

    # Crear el servicio (carga amistades existentes del JSON)
    servicio = ServicioSocial(repo, directorio, sesion)

    # Crear la vista
    VistaSocial(root, servicio)

    root.mainloop()


if __name__ == "__main__":
    main()
