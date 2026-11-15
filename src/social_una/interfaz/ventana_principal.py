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
        self.configure(bg="#F3F6FA")

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

        ancho = min(1100, max(640, self.winfo_screenwidth() - 40))
        alto = min(720, max(480, self.winfo_screenheight() - 80))

        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2

        self.minsize(min(760, ancho), min(540, alto))
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
                text=f"Hola, {nombre}" if nombre else "Bienvenido a Social UNA"
            )
        if (
            hasattr(self, "_etiqueta_usuario")
            and self._etiqueta_usuario.winfo_exists()
        ):
            self._etiqueta_usuario.config(
                text=f"Conectado: {nombre}" if nombre else ""
            )

    def _crear_interfaz(self):
        """Construye los componentes de la ventana principal."""

        estilo = ttk.Style(self)
        estilo.configure("Social.Sidebar.TFrame", background="#102A4C")
        estilo.configure(
            "Social.SidebarHeading.TLabel",
            background="#102A4C",
            foreground="#D7E2EF",
            font=("Segoe UI", 9, "bold"),
        )
        estilo.configure(
            "Social.Nav.TButton",
            background="#102A4C",
            foreground="#E7EEF7",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padding=(14, 12),
            borderwidth=0,
        )
        estilo.map(
            "Social.Nav.TButton",
            background=[("active", "#1D416B")],
            foreground=[("active", "white")],
        )
        estilo.configure(
            "Social.NavActive.TButton",
            background="#C8102E",
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padding=(14, 12),
            borderwidth=0,
        )
        estilo.map(
            "Social.NavActive.TButton",
            background=[("active", "#A90E27")],
            foreground=[("active", "white")],
        )
        estilo.configure(
            "Social.Logout.TButton",
            background="#C8102E",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            borderwidth=0,
        )
        estilo.map(
            "Social.Logout.TButton",
            background=[
                ("pressed", "#9E1028"),
                ("active", "#A90E27"),
            ],
            foreground=[("disabled", "#F8E8EB")],
        )

        barra_superior = tk.Frame(self, bg="#102A4C", padx=24, pady=8)
        barra_superior.pack(fill="x")

        marca = tk.Frame(barra_superior, bg="#102A4C")
        marca.pack(side="left")

        tk.Label(
            marca,
            text="UNA",
            bg="#102A4C",
            fg="#E31837",
            font=("Georgia", 36),
        ).pack(side="left", padx=(8, 15))

        tk.Frame(marca, bg="#D7E2EF", width=1, height=44).pack(
            side="left",
            padx=(0, 18),
        )

        identidad = tk.Frame(marca, bg="#102A4C")
        identidad.pack(side="left")
        tk.Label(
            identidad,
            text="Social UNA",
            bg="#102A4C",
            fg="white",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            identidad,
            text="Universidad Nacional",
            bg="#102A4C",
            fg="#D7E2EF",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        acciones_usuario = tk.Frame(barra_superior, bg="#102A4C")
        acciones_usuario.pack(side="right")

        self._etiqueta_usuario = tk.Label(
            acciones_usuario,
            text="",
            bg="#102A4C",
            fg="#E7EEF7",
            font=("Segoe UI", 10),
        )
        self._etiqueta_usuario.pack(side="left", padx=(0, 16))
        tk.Frame(acciones_usuario, bg="#506681", width=1, height=30).pack(
            side="left",
            padx=(0, 16),
        )

        self._btn_cerrar_sesion = ttk.Button(
            acciones_usuario,
            text="Cerrar sesión",
            style="Social.Logout.TButton",
            command=self._cerrar_sesion,
        )
        self._btn_cerrar_sesion.pack(side="left")

        self._lienzo_ondas_superior = tk.Canvas(
            barra_superior,
            bg="#102A4C",
            height=64,
            highlightthickness=0,
            bd=0,
        )
        self._lienzo_ondas_superior.pack(
            side="left",
            fill="both",
            expand=True,
            padx=14,
        )
        self._lienzo_ondas_superior.bind(
            "<Configure>",
            self._dibujar_ondas_superiores,
        )

        cuerpo = tk.Frame(self, bg="#F3F6FA")
        cuerpo.pack(fill="both", expand=True)

        barra_lateral = ttk.Frame(
            cuerpo,
            style="Social.Sidebar.TFrame",
            width=260,
        )
        barra_lateral.pack(side="left", fill="y")
        barra_lateral.pack_propagate(False)

        ttk.Label(
            barra_lateral,
            text="NAVEGACIÓN",
            style="Social.SidebarHeading.TLabel",
        ).pack(anchor="w", padx=20, pady=(27, 12))

        self._btn_publicaciones = ttk.Button(
            barra_lateral,
            text="Publicaciones",
            style="Social.NavActive.TButton",
            command=self._mostrar_publicaciones,
        )
        self._btn_publicaciones.pack(
            fill="x",
            padx=10,
            pady=3,
        )

        self._btn_amistades = ttk.Button(
            barra_lateral,
            text="Amistades y búsqueda",
            style="Social.Nav.TButton",
            command=self._mostrar_amistades,
        )
        self._btn_amistades.pack(
            fill="x",
            padx=10,
            pady=3,
        )

        tk.Frame(
            barra_lateral,
            bg="#385372",
            height=1,
        ).pack(fill="x", padx=18, pady=20)

        tk.Label(
            barra_lateral,
            text="Conectá con tu comunidad universitaria.",
            bg="#102A4C",
            fg="#D7E2EF",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=160,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        contenido = tk.Frame(
            cuerpo,
            bg="#F3F6FA",
            padx=20,
            pady=16,
        )
        contenido.pack(side="left", fill="both", expand=True)

        tarjeta_bienvenida = tk.Frame(
            contenido,
            bg="white",
            highlightthickness=1,
            highlightbackground="#CFE0F1",
        )
        tarjeta_bienvenida.pack(fill="x", pady=(0, 14))

        tk.Frame(
            tarjeta_bienvenida,
            bg="#C8102E",
            width=4,
        ).pack(side="left", fill="y")

        icono_usuario = tk.Canvas(
            tarjeta_bienvenida,
            width=62,
            height=62,
            bg="white",
            highlightthickness=0,
        )
        icono_usuario.pack(side="left", padx=(12, 4), pady=8)
        icono_usuario.create_oval(21, 8, 40, 27, fill="#C8102E", outline="")
        icono_usuario.create_arc(
            8, 25, 53, 61,
            start=0,
            extent=180,
            fill="#C8102E",
            outline="",
            style=tk.PIESLICE,
        )

        texto_bienvenida = tk.Frame(tarjeta_bienvenida, bg="white")
        texto_bienvenida.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8,
            pady=15,
        )

        self._etiqueta_bienvenida = tk.Label(
            texto_bienvenida,
            text="Bienvenido a Social UNA",
            bg="white",
            fg="#102A4C",
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        )
        self._etiqueta_bienvenida.pack(anchor="w")

        tk.Label(
            texto_bienvenida,
            text="Conectá con tu comunidad universitaria.",
            bg="white",
            fg="#64748B",
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

        self._lienzo_campus = tk.Canvas(
            tarjeta_bienvenida,
            width=230,
            height=82,
            bg="white",
            highlightthickness=0,
        )
        self._lienzo_campus.pack(side="right", padx=(8, 12), pady=(8, 0))
        self._dibujar_campus()

        panel_seccion = tk.Frame(
            contenido,
            bg="white",
            highlightthickness=1,
            highlightbackground="#CFE0F1",
        )
        panel_seccion.pack(fill="both", expand=True)

        self._encabezado_seccion = tk.Frame(panel_seccion, bg="white")
        self._encabezado_seccion.pack(fill="x", padx=18, pady=(11, 0))

        icono_seccion = tk.Canvas(
            self._encabezado_seccion,
            width=29,
            height=29,
            bg="white",
            highlightthickness=0,
        )
        icono_seccion.pack(side="left", padx=(0, 10))
        icono_seccion.create_rectangle(
            3, 4, 25, 24,
            outline="#C8102E",
            width=2,
        )
        icono_seccion.create_line(
            8, 10, 20, 10,
            fill="#C8102E",
            width=2,
        )
        icono_seccion.create_line(
            8, 15, 18, 15,
            fill="#C8102E",
            width=2,
        )

        self._etiqueta_seccion = tk.Label(
            self._encabezado_seccion,
            text="Publicaciones",
            bg="white",
            fg="#102A4C",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        )
        self._etiqueta_seccion.pack(side="left", anchor="w")

        self._linea_seccion = tk.Frame(panel_seccion, bg="#D8E3EF", height=1)
        self._linea_seccion.pack(fill="x", padx=18, pady=(10, 0))
        self._acento_seccion = tk.Frame(
            panel_seccion,
            bg="#C8102E",
            height=4,
            width=68,
        )
        self._acento_seccion.pack(anchor="w", padx=18)

        self._barra_contenido = ttk.Scrollbar(
            panel_seccion,
            orient="vertical",
        )
        self._lienzo_contenido = tk.Canvas(
            panel_seccion,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        self._lienzo_contenido.configure(
            yscrollcommand=self._barra_contenido.set,
        )
        self._area_contenido = tk.Frame(self._lienzo_contenido, bg="white")
        self._area_contenido.pack_propagate(False)
        self._ventana_area_contenido = self._lienzo_contenido.create_window(
            (0, 0),
            window=self._area_contenido,
            anchor="nw",
        )
        self._area_contenido.bind(
            "<Configure>",
            self._programar_ajuste_contenido,
        )
        self._lienzo_contenido.bind(
            "<Configure>",
            self._programar_ajuste_contenido,
        )
        self._lienzo_contenido.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0),
            pady=(4, 8),
        )
        self._barra_contenido.configure(
            command=self._lienzo_contenido.yview,
        )
        self._barra_contenido_visible = False
        self._ajuste_contenido_programado = None

    def _dibujar_ondas_superiores(self, evento):
        """Dibuja ondas institucionales discretas en la barra superior."""

        lienzo = self._lienzo_ondas_superior
        lienzo.delete("onda")
        ancho = evento.width
        alto = evento.height
        if ancho < 40 or alto < 20:
            return

        puntos = (
            0, alto * 0.78,
            ancho * 0.22, alto * 0.70,
            ancho * 0.47, alto * 0.25,
            ancho * 0.72, alto * 0.13,
            ancho, alto * 0.08,
        )
        lienzo.create_line(
            *puntos,
            smooth=True,
            splinesteps=32,
            fill="#FFFFFF",
            width=5,
            tags="onda",
        )
        lienzo.create_line(
            0, alto * 0.86,
            ancho * 0.22, alto * 0.78,
            ancho * 0.47, alto * 0.33,
            ancho * 0.72, alto * 0.21,
            ancho, alto * 0.16,
            smooth=True,
            splinesteps=32,
            fill="#E31837",
            width=7,
            tags="onda",
        )

    def _dibujar_campus(self):
        """Ilustra el campus con formas vectoriales ligeras de Tkinter."""

        lienzo = self._lienzo_campus
        lienzo.delete("all")
        linea = "#B7CDE3"
        relleno = "#ECF3FA"
        lienzo.create_rectangle(53, 38, 178, 76, fill=relleno, outline=linea, width=2)
        lienzo.create_polygon(
            43, 39, 114, 7, 188, 39,
            fill="#F8FBFE",
            outline=linea,
            width=2,
        )
        lienzo.create_text(
            115, 29,
            text="UNA",
            fill="#9DB6D0",
            font=("Georgia", 10, "bold"),
        )
        for x in (66, 87, 143, 164):
            lienzo.create_rectangle(
                x, 47, x + 10, 59,
                fill="#D9E7F4",
                outline=linea,
            )
        lienzo.create_rectangle(105, 50, 125, 76, fill="#D9E7F4", outline=linea)
        for x, y in ((27, 49), (203, 47)):
            lienzo.create_rectangle(
                x - 2, y + 15, x + 2, 77,
                fill=linea,
                outline="",
            )
            lienzo.create_oval(
                x - 16, y - 2, x + 16, y + 24,
                fill=relleno,
                outline=linea,
            )
        lienzo.create_line(20, 77, 212, 77, fill=linea, width=2)

    def _actualizar_navegacion(self, seccion: str):
        """Resalta la sección que se encuentra visible."""

        self._btn_publicaciones.configure(
            style=(
                "Social.NavActive.TButton"
                if seccion == "publicaciones"
                else "Social.Nav.TButton"
            )
        )
        self._btn_amistades.configure(
            style=(
                "Social.NavActive.TButton"
                if seccion == "amistades"
                else "Social.Nav.TButton"
            )
        )

    def _programar_ajuste_contenido(self, evento=None):
        """Pospone el cálculo de scroll hasta completar el layout de Tk."""

        if (
            evento is not None
            and evento.widget is self._lienzo_contenido
        ):
            self._lienzo_contenido.itemconfigure(
                self._ventana_area_contenido,
                width=max(evento.width, 1),
            )
        if self._ajuste_contenido_programado is None:
            self._ajuste_contenido_programado = self.after_idle(
                self._ajustar_contenido
            )

    def _ajustar_contenido(self):
        """Ajusta el alto de la vista y muestra scroll si no cabe en el panel."""

        self._ajuste_contenido_programado = None
        if not self._lienzo_contenido.winfo_exists():
            return

        self._area_contenido.update_idletasks()
        vistas = self._area_contenido.winfo_children()
        alto_solicitado = max(
            (vista.winfo_reqheight() for vista in vistas),
            default=0,
        )
        alto_visible = max(self._lienzo_contenido.winfo_height(), 1)
        necesita_scroll = alto_solicitado > alto_visible

        if necesita_scroll != self._barra_contenido_visible:
            self._barra_contenido_visible = necesita_scroll
            if necesita_scroll:
                self._barra_contenido.pack(
                    side="right",
                    fill="y",
                    pady=(4, 8),
                )
            else:
                self._barra_contenido.pack_forget()
            self._programar_ajuste_contenido()
            return

        ancho = max(self._lienzo_contenido.winfo_width(), 1)
        alto = max(alto_visible, alto_solicitado)
        self._lienzo_contenido.itemconfigure(
            self._ventana_area_contenido,
            width=ancho,
            height=alto,
        )
        self._lienzo_contenido.configure(
            scrollregion=(0, 0, ancho, alto),
        )
        if not necesita_scroll:
            self._lienzo_contenido.yview_moveto(0)

    # ---------------------------------------------------------
    # Navegacion entre vistas
    # ---------------------------------------------------------

    def _limpiar_area_contenido(self):
        """Elimina los widgets del area de contenido."""

        for widget in self._area_contenido.winfo_children():
            widget.destroy()

    def _mostrar_encabezado_seccion(self, visible):
        if visible:
            self._encabezado_seccion.pack(
                fill="x",
                padx=18,
                pady=(11, 0),
                before=self._lienzo_contenido,
            )
            self._linea_seccion.pack(
                fill="x",
                padx=18,
                pady=(10, 0),
                before=self._lienzo_contenido,
            )
            self._acento_seccion.pack(
                anchor="w",
                padx=18,
                before=self._lienzo_contenido,
            )
            return

        self._encabezado_seccion.pack_forget()
        self._linea_seccion.pack_forget()
        self._acento_seccion.pack_forget()

    def _mostrar_publicaciones(self):
        """Muestra la vista del muro de publicaciones."""

        self._limpiar_area_contenido()
        self._mostrar_encabezado_seccion(True)
        self._actualizar_navegacion("publicaciones")
        self._etiqueta_seccion.config(text="Publicaciones")

        self._vista_muro = VistaMuro(
            self._area_contenido,
            self._servicio_publicaciones,
        )

        self._vista_muro.pack(
            fill="both",
            expand=True,
        )

        self._vista_muro.refrescar()
        self._programar_ajuste_contenido()
        self._lienzo_contenido.yview_moveto(0)

        self.title("Social UNA - Publicaciones")

    def _mostrar_amistades(self):
        """Muestra la vista de amistades."""

        self._limpiar_area_contenido()
        self._mostrar_encabezado_seccion(False)
        self._actualizar_navegacion("amistades")
        self._etiqueta_seccion.config(text="Amistades y búsqueda")

        self._vista_social = VistaSocial(
            self._area_contenido,
            self._servicio_social,
        )

        self._vista_social.pack(
            fill="both",
            expand=True,
        )

        self._vista_social.refrescar()
        self._programar_ajuste_contenido()
        self._lienzo_contenido.yview_moveto(0)

        self.title("Social UNA - Amistades")

    
    # ---------------------------------------------------------
    # Cierre de sesion
    # ---------------------------------------------------------

    def _cerrar_sesion(self):
        """Cierra la sesion y regresa a la ventana de acceso."""

        if self._cerrando:
            return

        confirmar = messagebox.askyesno(
            "Cerrar sesión",
            "¿Desea cerrar su sesión?",
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
