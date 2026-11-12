import tkinter as tk
from tkinter import ttk, messagebox

from social_una.dominio.errores import ErrorSocialUna
from social_una.interfaz.vista_muro import VistaMuro
from social_una.interfaz.vista_social import VistaSocial


class VentanaPrincipal(tk.Toplevel):
    """Ventana principal de Social UNA despues de iniciar sesion."""

    def __init__(
        self,
        ventana_padre,
        servicio_autenticacion,
        servicio_social,
        servicio_publicaciones,
        sesion,
    ):
        super().__init__(ventana_padre)

        self._servicio_autenticacion = servicio_autenticacion
        self._servicio_social = servicio_social
        self._servicio_publicaciones = servicio_publicaciones
        self._sesion = sesion
        self._cerrando = False

        self.title("Social UNA - Inicio")
        self.geometry("850x550")
        self.minsize(700, 450)
        self.configure(bg="#eef2f7")

        self._centrar_ventana()
        self._crear_interfaz()

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cerrar_sesion,
        )

        self._actualizar_bienvenida()
        self._mostrar_publicaciones()

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla."""

        self.update_idletasks()

        ancho = 850
        alto = 550

        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2

        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _usuario_actual_nombre(self) -> str:
        """Devuelve el nombre del usuario actual de la sesion."""

        try:
            return self._sesion.usuario_actual().nombre
        except ErrorSocialUna:
            return ""

    def _actualizar_bienvenida(self):
        """Actualiza la etiqueta de bienvenida."""

        nombre = self._usuario_actual_nombre()

        if (
            hasattr(self, "_etiqueta_bienvenida")
            and self._etiqueta_bienvenida.winfo_exists()
        ):
            self._etiqueta_bienvenida.config(
                text=f"Hola, {nombre}" if nombre else ""
            )

    def _crear_interfaz(self):
        """Construye los componentes de la ventana principal."""

        contenido = tk.Frame(
            self,
            bg="#eef2f7",
            padx=35,
            pady=30,
        )
        contenido.pack(fill="both", expand=True)

        self._etiqueta_bienvenida = tk.Label(
            contenido,
            text="Bienvenido a Social UNA",
            bg="#eef2f7",
            fg="#17365d",
            font=("Arial", 22, "bold"),
        )
        self._etiqueta_bienvenida.pack(
            anchor="w",
            pady=(5, 8),
        )

        tk.Label(
            contenido,
            text="Tu espacio de conexion con la comunidad universitaria.",
            bg="#eef2f7",
            fg="#64748b",
            font=("Arial", 11),
        ).pack(anchor="w", pady=(0, 25))

        # Opciones de navegacion.
        opciones = tk.Frame(
            contenido,
            bg="#eef2f7",
        )
        opciones.pack(fill="x", pady=20)

        estilo = ttk.Style(self)
        estilo.configure(
            "Opcion.TButton",
            font=("Arial", 11, "bold"),
            padding=15,
        )

        self._btn_publicaciones = ttk.Button(
            opciones,
            text="Publicaciones",
            style="Opcion.TButton",
            command=self._mostrar_publicaciones,
        )
        self._btn_publicaciones.pack(
            side="left",
            expand=True,
            fill="x",
            padx=(0, 8),
        )

        self._btn_amistades = ttk.Button(
            opciones,
            text="Amistades",
            style="Opcion.TButton",
            command=self._mostrar_amistades,
        )
        self._btn_amistades.pack(
            side="left",
            expand=True,
            fill="x",
            padx=8,
        )

        ttk.Button(
            opciones,
            text="Cerrar sesion",
            style="Opcion.TButton",
            command=self._cerrar_sesion,
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=(8, 0),
        )

        # Area de contenido dinamico.
        self._area_contenido = tk.Frame(
            contenido,
            bg="#eef2f7",
        )
        self._area_contenido.pack(
            fill="both",
            expand=True,
        )

        tk.Label(
            contenido,
            text=(
                "Seleccione una seccion para ver su contenido. "
                "Las vistas se refrescan al cambiar de seccion."
            ),
            bg="#eef2f7",
            fg="#64748b",
            font=("Arial", 9),
            wraplength=750,
        ).pack(anchor="w", pady=10)

    # ---------------------------------------------------------
    # Navegacion entre vistas
    # ---------------------------------------------------------

    def _limpiar_area_contenido(self):
        """Elimina los widgets del area de contenido."""

        for widget in self._area_contenido.winfo_children():
            widget.destroy()

    def _mostrar_publicaciones(self):
        """Muestra la vista del muro de publicaciones."""

        self._limpiar_area_contenido()

        self._vista_muro = VistaMuro(
            self._area_contenido,
            self._servicio_publicaciones,
        )

        self._vista_muro.pack(
            fill="both",
            expand=True,
        )

        self._vista_muro.refrescar()

        self.title("Social UNA - Publicaciones")

    def _mostrar_amistades(self):
        """Muestra la vista de amistades."""

        self._limpiar_area_contenido()

        # VistaSocial coloca sus propios componentes dentro del contenedor.
        # No necesita llamar a pack() sobre el objeto VistaSocial.
        self._vista_social = VistaSocial(
            self._area_contenido,
            self._servicio_social,
        )

        self.title("Social UNA - Amistades")

    # ---------------------------------------------------------
    # Cierre de sesion
    # ---------------------------------------------------------

    def _cerrar_sesion(self):
        """Cierra la sesion y regresa a la ventana de acceso."""

        if self._cerrando:
            return

        confirmar = messagebox.askyesno(
            "Cerrar sesion",
            "¿Desea cerrar su sesion?",
            parent=self,
        )

        if not confirmar:
            return

        self._cerrando = True

        try:
            self._servicio_autenticacion.cerrar_sesion()

            padre = self.master

            self.destroy()

            if padre is not None and hasattr(
                padre,
                "volver_al_login",
            ):
                padre.volver_al_login()

        except ErrorSocialUna as error:
            self._cerrando = False

            messagebox.showerror(
                "Error",
                f"No se pudo cerrar la sesion: {error}",
                parent=self,
            )
