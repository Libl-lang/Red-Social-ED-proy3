"""Lanzador de desarrollo que muestra la pantalla del muro con piezas falsas, para probarla sin esperar a los otros módulos; se ejecuta con F5."""

import tkinter as tk
from tkinter import ttk
from pruebas.falsos.consulta_amistades_falsa import ConsultaAmistadesFalsa
from pruebas.falsos.directorio_usuarios_falso import USUARIOS_FALSOS, DirectorioUsuariosFalso
from pruebas.falsos.repositorios_en_memoria import RepositorioPublicacionesEnMemoria
from pruebas.falsos.sesion_falsa import SesionFalsa
from social_una.dominio.modelos import Publicacion
from social_una.interfaz.vista_muro import VistaMuro
from social_una.servicios.servicio_publicaciones import ServicioPublicaciones


def main() -> None:
    # 1) Crea la lista publicaciones con estas cuatro, en este orden y con argumentos posicionales (id_publicacion, id_autor, texto, fecha_creacion):
    publicaciones = [
        Publicacion(1, 2, "Hola desde Beto", "2026-11-03T09:00:00+00:00"),
        Publicacion(2, 3, "Mensaje de Carla", "2026-11-03T10:00:00+00:00"),
        Publicacion(3, 2, "Segundo mensaje de Beto", "2026-11-03T11:00:00+00:00"),
        Publicacion(4, 1, "Publicación de Ana", "2026-11-03T12:00:00+00:00"),
    ]
    # 2) Crea repositorio = RepositorioPublicacionesEnMemoria(publicaciones) y sesion = SesionFalsa().
    repositorio = RepositorioPublicacionesEnMemoria(publicaciones)
    sesion = SesionFalsa()
    # 3) Crea servicio = ServicioPublicaciones(repositorio, ConsultaAmistadesFalsa(), DirectorioUsuariosFalso(), sesion).
    servicio = ServicioPublicaciones(repositorio, ConsultaAmistadesFalsa(), DirectorioUsuariosFalso(), sesion)
    # 4) Crea raiz = tk.Tk(), con raiz.title("Social UNA - Muro (modo desarrollo)") y raiz.geometry("560x600").
    raiz = tk.Tk()
    raiz.title("Social UNA - Muro (modo desarrollo)")
    raiz.geometry("560x600")
    # 5) Crea vista = VistaMuro(raiz, servicio).
    vista = VistaMuro(raiz, servicio)
    # 6) Define una función interna cambiar_usuario(usuario) que ejecuta sesion.iniciar_como(usuario) y luego vista.refrescar(). Debe estar definida ANTES de crear los botones.
    def cambiar_usuario(usuario):
        sesion.iniciar_como(usuario)
        vista.refrescar()
    # 7) Crea un ttk.Frame (barra) con barra.pack(fill="x", padx=8, pady=4). Dentro, un ttk.Label con text="Ver como:" (side="left") y, por cada usuario de USUARIOS_FALSOS, un ttk.Button con text=usuario.nombre y command=lambda u=usuario: cambiar_usuario(u), empaquetado con side="left", padx=2.
    barra = ttk.Frame(raiz)
    barra.pack(fill="x", padx=8, pady=4)
    ttk.Label(barra, text="Ver como:").pack(side="left")
    for usuario in USUARIOS_FALSOS:
        ttk.Button(barra, text=usuario.nombre, command=lambda u=usuario: cambiar_usuario(u)).pack(side="left", padx=2)
    # 8) Empaqueta la vista con vista.pack(fill="both", expand=True, padx=8, pady=8), llama a vista.refrescar() y luego a raiz.mainloop().
    vista.pack(fill="both", expand=True, padx=8, pady=8)
    vista.refrescar()
    raiz.mainloop()


if __name__ == "__main__":
    main()
