import math
import tkinter as tk
from tkinter import ttk, messagebox

from social_una.dominio.errores import (
    ErrorAutenticacion,
    ErrorValidacion,
    ErrorDuplicado,
    ErrorAlmacenamiento,
)


class VistaAutenticacion(tk.Tk):
    """Ventana de inicio de sesion y registro de Social UNA."""

    def __init__(self, servicio_autenticacion, al_iniciar_sesion):
        super().__init__()

        self._servicio = servicio_autenticacion
        self._al_iniciar_sesion = al_iniciar_sesion
        self.title("Social UNA - Acceso")
        self.configure(bg="#102A4C")
        self.resizable(True, True)

        self._centrar_ventana()
        self._configurar_estilos()
        self.mostrar_login()

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla."""

        self.update_idletasks()

        ancho = min(960, max(420, self.winfo_screenwidth() - 48))
        alto = min(760, max(560, self.winfo_screenheight() - 96))

        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2

        self.minsize(min(420, ancho), min(560, alto))
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _configurar_estilos(self):
        """Configura los estilos visuales."""

        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(
            "Auth.Title.TLabel",
            background="white",
            foreground="#102A4C",
            font=("Segoe UI", 32, "bold"),
        )

        estilo.configure(
            "Auth.Subtitle.TLabel",
            background="white",
            foreground="#64748B",
            font=("Segoe UI", 13),
        )

        estilo.configure(
            "Auth.Field.TLabel",
            background="white",
            foreground="#243B53",
            font=("Segoe UI", 14, "bold"),
        )

        estilo.configure(
            "Auth.TEntry",
            fieldbackground="#F8FAFC",
            foreground="#102A4C",
            padding=(12, 9),
            bordercolor="#CBD5E1",
            lightcolor="#CBD5E1",
            darkcolor="#CBD5E1",
            insertcolor="#102A4C",
        )

        estilo.map(
            "Auth.TEntry",
            bordercolor=[("focus", "#2B6CB0")],
            lightcolor=[("focus", "#2B6CB0")],
            darkcolor=[("focus", "#2B6CB0")],
        )

        estilo.configure(
            "Auth.Primary.TButton",
            background="#1D5FA7",
            foreground="white",
            font=("Segoe UI", 12, "bold"),
            padding=(12, 10),
            borderwidth=0,
            focusthickness=2,
            focuscolor="#8FBCE6",
        )
        estilo.map(
            "Auth.Primary.TButton",
            background=[
                ("pressed", "#164B86"),
                ("active", "#174F8D"),
            ],
            foreground=[("disabled", "#E2E8F0")],
        )

        estilo.configure(
            "Auth.Secondary.TButton",
            background="white",
            foreground="#B4233A",
            font=("Segoe UI", 12, "bold"),
            padding=(12, 10),
            borderwidth=1,
            relief="solid",
            focusthickness=2,
            focuscolor="#E9A3AE",
        )
        estilo.map(
            "Auth.Secondary.TButton",
            background=[("pressed", "#FFF1F2"), ("active", "#FFF7F7")],
            foreground=[("pressed", "#8F1D30"), ("active", "#8F1D30")],
        )

        estilo.configure(
            "Auth.Password.TButton",
            background="#F1F5F9",
            foreground="#1D5FA7",
            font=("Segoe UI", 10, "bold"),
            padding=(9, 8),
            borderwidth=0,
        )
        estilo.map(
            "Auth.Password.TButton",
            background=[("pressed", "#E2E8F0"), ("active", "#E8EEF5")],
        )

        estilo.configure(
            "Auth.Section.TLabel",
            background="white",
            foreground="#243B53",
            font=("Segoe UI", 17, "bold"),
        )

    def _limpiar_ventana(self):
        """Elimina los componentes de la vista actual."""

        for componente in self.winfo_children():
            componente.destroy()

    def _crear_encabezado(self, subtitulo):
        """Construye el encabezado de la ventana."""

        titulo = tk.Frame(self.panel, bg="white")
        titulo.pack(fill="x")

        icono = tk.Canvas(
            titulo,
            width=64,
            height=56,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        icono.pack(side="left", padx=(0, 9))
        icono.create_oval(8, 6, 27, 25, fill="#102A4C", outline="")
        icono.create_oval(34, 9, 50, 25, fill="#102A4C", outline="")
        icono.create_arc(
            2, 24, 34, 54, start=0, extent=180,
            fill="#102A4C", outline="", style=tk.PIESLICE,
        )
        icono.create_arc(
            28, 27, 56, 53, start=0, extent=180,
            fill="#102A4C", outline="", style=tk.PIESLICE,
        )

        ttk.Label(
            titulo,
            text="Social UNA",
            style="Auth.Title.TLabel",
        ).pack(side="left", anchor="center")

        ttk.Label(
            self.panel,
            text="Red social estudiantil de la UNA",
            style="Auth.Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        seccion = tk.Frame(self.panel, bg="white")
        seccion.pack(fill="x", pady=(12, 8))
        ttk.Separator(seccion, orient="horizontal").pack(
            side="left", fill="x", expand=True, padx=(0, 20)
        )
        ttk.Label(
            seccion,
            text=subtitulo,
            style="Auth.Section.TLabel",
        ).pack(side="left")
        ttk.Separator(seccion, orient="horizontal").pack(
            side="left", fill="x", expand=True, padx=(20, 0)
        )

    def volver_al_login(self):
        """Vuelve a mostrar la ventana de acceso."""

        self.deiconify()
        self.mostrar_login()

    def _alternar_contrasena(self, campo, boton, atributo_estado):
        """Muestra u oculta la contraseña del campo indicado."""

        visible = not getattr(self, atributo_estado, False)
        setattr(self, atributo_estado, visible)

        campo.configure(show="" if visible else "*")
        boton.configure(text="Ocultar" if visible else "Mostrar")

    def _crear_marco_principal(self):
        """Crea el fondo decorativo, el logo y la tarjeta del formulario."""

        self._marco_scroll = tk.Frame(self, bg="#102A4C")
        self._marco_scroll.pack(fill="both", expand=True)

        self._lienzo_fondo = tk.Canvas(
            self._marco_scroll,
            bg="#102A4C",
            highlightthickness=0,
            bd=0,
        )
        self._lienzo_fondo.pack(side="left", fill="both", expand=True)
        self._barra_scroll = ttk.Scrollbar(
            self._marco_scroll,
            orient="vertical",
            command=self._lienzo_fondo.yview,
        )
        self._lienzo_fondo.configure(yscrollcommand=self._barra_scroll.set)
        self._barra_scroll_visible = False
        self._ajuste_programado = None
        self._lienzo_fondo.bind("<Configure>", self._ajustar_presentacion)
        self._lienzo_fondo.bind("<MouseWheel>", self._desplazar_contenido)

        self._contenedor = tk.Frame(self._lienzo_fondo, bg="#102A4C")
        self._contenedor.pack_propagate(False)
        self._ventana_contenido = self._lienzo_fondo.create_window(
            (0, 0),
            window=self._contenedor,
            anchor="n",
            tags="contenido",
        )

        self._encabezado_institucional = tk.Frame(
            self._contenedor,
            bg="#102A4C",
        )
        self._encabezado_institucional.pack(fill="x", pady=(0, 22))

        tk.Label(
            self._encabezado_institucional,
            text="UNA",
            bg="#102A4C",
            fg="#E33B50",
            font=("Georgia", 52),
        ).pack()

        tk.Label(
            self._encabezado_institucional,
            text="Universidad Nacional",
            bg="#102A4C",
            fg="#FFFFFF",
            font=("Segoe UI", 15),
        ).pack()

        self._tarjeta = tk.Canvas(
            self._contenedor,
            bg="#102A4C",
            highlightthickness=0,
            bd=0,
        )
        self._tarjeta.pack(fill="x", padx=3)
        self._tarjeta.bind("<Configure>", self._dibujar_tarjeta)

        self.panel = tk.Frame(self._tarjeta, bg="white", padx=40, pady=20)
        self._ventana_panel = self._tarjeta.create_window(
            (15, 15),
            window=self.panel,
            anchor="nw",
            tags="panel",
        )
        self._ancho_panel_aplicado = None
        self._tarjeta.after_idle(self._actualizar_tarjeta)

    @staticmethod
    def _puntos_redondeados(x1, y1, x2, y2, radio):
        """Devuelve puntos para una forma rectangular con esquinas curvas."""

        puntos = []
        for centro_x, centro_y, inicio in (
            (x2 - radio, y1 + radio, -90),
            (x2 - radio, y2 - radio, 0),
            (x1 + radio, y2 - radio, 90),
            (x1 + radio, y1 + radio, 180),
        ):
            for paso in range(7):
                angulo = math.radians(inicio + paso * 90 / 6)
                puntos.extend(
                    (
                        centro_x + radio * math.cos(angulo),
                        centro_y + radio * math.sin(angulo),
                    )
                )
        return puntos

    def _dibujar_tarjeta(self, evento=None):
        """Dibuja sombra, borde y superficie redondeada de la tarjeta."""

        ancho = max(
            evento.width if evento is not None else self._tarjeta.winfo_width(),
            1,
        )
        alto = max(
            evento.height if evento is not None else self._tarjeta.winfo_height(),
            1,
        )
        ancho_panel = max(ancho - 30, 1)
        self._tarjeta.itemconfigure(self._ventana_panel, width=ancho_panel)
        if ancho_panel != self._ancho_panel_aplicado:
            self._ancho_panel_aplicado = ancho_panel
            self._tarjeta.after_idle(self._actualizar_tarjeta)
        self._tarjeta.delete("forma")

        sombra = self._puntos_redondeados(
            7, 8, ancho - 3, alto - 5, 17
        )
        borde = self._puntos_redondeados(
            3, 2, ancho - 7, alto - 11, 17
        )
        self._tarjeta.create_polygon(
            sombra,
            smooth=True,
            splinesteps=24,
            fill="#0B1E35",
            outline="",
            tags="forma",
        )
        self._tarjeta.create_polygon(
            borde,
            smooth=True,
            splinesteps=24,
            fill="#D6DEE8",
            outline="",
            tags="forma",
        )
        self._tarjeta.create_polygon(
            self._puntos_redondeados(
                4, 3, ancho - 9, alto - 13, 15
            ),
            smooth=True,
            splinesteps=24,
            fill="white",
            outline="",
            tags="forma",
        )
        self._tarjeta.tag_lower("forma")

    def _actualizar_tarjeta(self):
        """Ajusta el tamaño de la tarjeta al contenido del formulario."""

        if not self.panel.winfo_exists() or not self._tarjeta.winfo_exists():
            return

        ancho_panel = max(self._tarjeta.winfo_width() - 30, 1)
        self._tarjeta.itemconfigure(self._ventana_panel, width=ancho_panel)
        self._tarjeta.update_idletasks()
        alto_panel = self.panel.winfo_reqheight()
        self._tarjeta.itemconfigure(
            self._ventana_panel,
            height=alto_panel,
        )
        self._tarjeta.configure(height=alto_panel + 30)
        self._dibujar_tarjeta()
        self._ajustar_contenedor()

    def _dibujar_ondas(self, ancho, alto):
        """Dibuja cintas onduladas detrás del encabezado y la tarjeta."""

        lienzo = self._lienzo_fondo
        lienzo.delete("ondas")
        if ancho < 2 or alto < 2:
            return

        lienzo.create_polygon(
            -20, alto * 0.37,
            ancho * 0.12, alto * 0.34,
            ancho * 0.32, alto * 0.38,
            ancho * 0.53, alto * 0.41,
            ancho * 0.75, alto * 0.38,
            ancho + 20, alto * 0.34,
            ancho + 20, alto + 20,
            -20, alto + 20,
            smooth=True,
            splinesteps=36,
            fill="#E8F1FB",
            outline="",
            tags="ondas",
        )
        lienzo.create_line(
            -20, alto * 0.245,
            ancho * 0.16, alto * 0.205,
            ancho * 0.38, alto * 0.245,
            ancho * 0.63, alto * 0.26,
            ancho * 0.82, alto * 0.225,
            ancho + 20, alto * 0.17,
            smooth=True,
            splinesteps=40,
            fill="#FFFFFF",
            width=9,
            tags="ondas",
        )
        lienzo.create_line(
            -20, alto * 0.262,
            ancho * 0.16, alto * 0.222,
            ancho * 0.38, alto * 0.262,
            ancho * 0.63, alto * 0.277,
            ancho * 0.82, alto * 0.242,
            ancho + 20, alto * 0.187,
            smooth=True,
            splinesteps=40,
            fill="#E31837",
            width=12,
            tags="ondas",
        )
        lienzo.create_polygon(
            -20, alto * 0.925,
            ancho * 0.13, alto * 0.89,
            ancho * 0.31, alto * 0.925,
            ancho * 0.52, alto * 0.955,
            ancho * 0.75, alto * 0.935,
            ancho + 20, alto * 0.895,
            ancho + 20, alto + 20,
            -20, alto + 20,
            smooth=True,
            splinesteps=40,
            fill="#102A4C",
            outline="",
            tags="ondas",
        )
        lienzo.create_line(
            -20, alto * 0.912,
            ancho * 0.13, alto * 0.877,
            ancho * 0.31, alto * 0.912,
            ancho * 0.52, alto * 0.942,
            ancho * 0.75, alto * 0.922,
            ancho + 20, alto * 0.882,
            smooth=True,
            splinesteps=40,
            fill="#E31837",
            width=9,
            tags="ondas",
        )
        lienzo.create_line(
            -20, alto * 0.895,
            ancho * 0.13, alto * 0.86,
            ancho * 0.31, alto * 0.895,
            ancho * 0.52, alto * 0.925,
            ancho * 0.75, alto * 0.905,
            ancho + 20, alto * 0.865,
            smooth=True,
            splinesteps=40,
            fill="#FFFFFF",
            width=4,
            tags="ondas",
        )
        lienzo.tag_lower("ondas")

    def _ajustar_contenedor(self):
        """Centra el contenido o activa scroll si el formulario no cabe."""

        if not self._lienzo_fondo.winfo_exists():
            return
        self._contenedor.update_idletasks()
        ancho = max(self._lienzo_fondo.winfo_width(), 1)
        alto = max(self._lienzo_fondo.winfo_height(), 1)
        ancho_contenido = min(880, max(400, ancho - 48))
        alto_contenido = (
            self._encabezado_institucional.winfo_reqheight()
            + 22
            + self._tarjeta.winfo_reqheight()
        )
        necesita_scroll = alto_contenido + 32 > alto
        if necesita_scroll != self._barra_scroll_visible:
            self._barra_scroll_visible = necesita_scroll
            if necesita_scroll:
                self._barra_scroll.pack(side="right", fill="y")
            else:
                self._barra_scroll.pack_forget()
            self.after_idle(self._ajustar_contenedor)
            return

        ancho = max(self._lienzo_fondo.winfo_width(), 1)
        alto = max(self._lienzo_fondo.winfo_height(), 1)
        ancho_contenido = min(880, max(400, ancho - 48))
        self._contenedor.configure(
            width=ancho_contenido,
            height=alto_contenido,
        )
        self._lienzo_fondo.itemconfigure(
            self._ventana_contenido,
            width=ancho_contenido,
            height=alto_contenido,
        )
        y = 16 if necesita_scroll else max(16, (alto - alto_contenido) // 2)
        self._lienzo_fondo.coords(
            self._ventana_contenido,
            ancho // 2,
            y,
        )
        alto_region = max(alto, alto_contenido + 32)
        self._lienzo_fondo.configure(
            scrollregion=(0, 0, ancho, alto_region)
        )
        if not necesita_scroll:
            self._lienzo_fondo.yview_moveto(0)

    def _ajustar_presentacion(self, evento):
        """Redibuja ondas y recalcula el scroll al cambiar el tamaño."""

        self._dibujar_ondas(evento.width, evento.height)
        if self._ajuste_programado is None:
            self._ajuste_programado = self.after_idle(
                self._ejecutar_ajuste_presentacion
            )

    def _ejecutar_ajuste_presentacion(self):
        self._ajuste_programado = None
        self._ajustar_contenedor()

    def _desplazar_contenido(self, evento):
        """Permite recorrer el formulario con la rueda cuando aparece el scroll."""

        if self._barra_scroll_visible:
            self._lienzo_fondo.yview_scroll(
                int(-evento.delta / 120),
                "units",
            )
        return "break"

    def mostrar_login(self):
        """Muestra el formulario de inicio de sesion."""

        self._limpiar_ventana()
        self._crear_marco_principal()

        self._crear_encabezado("Inicia sesión en tu cuenta")

        ttk.Label(
            self.panel,
            text="Nombre de usuario",
            style="Auth.Field.TLabel",
        ).pack(anchor="w", pady=(4, 7))

        self.txt_usuario = ttk.Entry(
            self.panel,
            style="Auth.TEntry",
            font=("Segoe UI", 11),
        )
        self.txt_usuario.pack(fill="x")

        ttk.Label(
            self.panel,
            text="Contraseña",
            style="Auth.Field.TLabel",
        ).pack(anchor="w", pady=(14, 6))

        fila_contrasena = tk.Frame(self.panel, bg="white")
        fila_contrasena.pack(fill="x")

        self.txt_contrasena = ttk.Entry(
            fila_contrasena,
            style="Auth.TEntry",
            font=("Segoe UI", 11),
            show="*",
        )
        self.txt_contrasena.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        self._contrasena_visible_login = False

        self.btn_mostrar_login = ttk.Button(
            fila_contrasena,
            text="Mostrar",
            style="Auth.Password.TButton",
            command=lambda: self._alternar_contrasena(
                self.txt_contrasena,
                self.btn_mostrar_login,
                "_contrasena_visible_login",
            ),
        )
        self.btn_mostrar_login.pack(side="right")

        ttk.Button(
            self.panel,
            text="Iniciar sesión",
            style="Auth.Primary.TButton",
            command=self._iniciar_sesion,
        ).pack(fill="x", pady=(20, 8))

        ttk.Button(
            self.panel,
            text="Crear una cuenta nueva",
            style="Auth.Secondary.TButton",
            command=self.mostrar_registro,
        ).pack(fill="x")

        self.txt_usuario.focus_set()
        self.txt_usuario.delete(0, tk.END)
        self.txt_contrasena.delete(0, tk.END)

        self.bind(
            "<Return>",
            lambda evento: self._iniciar_sesion()
        )
        self._tarjeta.after_idle(self._actualizar_tarjeta)

    def mostrar_registro(self):
        """Muestra el formulario para registrar usuarios."""

        self._limpiar_ventana()
        self.unbind("<Return>")
        self._crear_marco_principal()

        self._crear_encabezado("Crea tu cuenta")

        ttk.Label(
            self.panel,
            text="Nombre completo",
            style="Auth.Field.TLabel",
        ).pack(anchor="w", pady=(3, 5))

        self.txt_nombre = ttk.Entry(
            self.panel,
            style="Auth.TEntry",
            font=("Segoe UI", 11),
        )
        self.txt_nombre.pack(fill="x")

        ttk.Label(
            self.panel,
            text="Nombre de usuario",
            style="Auth.Field.TLabel",
        ).pack(anchor="w", pady=(9, 5))

        self.txt_usuario_registro = ttk.Entry(
            self.panel,
            style="Auth.TEntry",
            font=("Segoe UI", 11),
        )
        self.txt_usuario_registro.pack(fill="x")

        ttk.Label(
            self.panel,
            text="Contraseña (mínimo 6 caracteres)",
            style="Auth.Field.TLabel",
        ).pack(anchor="w", pady=(9, 5))

        fila_contrasena = tk.Frame(self.panel, bg="white")
        fila_contrasena.pack(fill="x")

        self.txt_contrasena_registro = ttk.Entry(
            fila_contrasena,
            style="Auth.TEntry",
            font=("Segoe UI", 11),
            show="*",
        )
        self.txt_contrasena_registro.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        self._contrasena_visible_registro = False

        self.btn_mostrar_registro = ttk.Button(
            fila_contrasena,
            text="Mostrar",
            style="Auth.Password.TButton",
            command=lambda: self._alternar_contrasena(
                self.txt_contrasena_registro,
                self.btn_mostrar_registro,
                "_contrasena_visible_registro",
            ),
        )
        self.btn_mostrar_registro.pack(side="right")

        ttk.Button(
            self.panel,
            text="Registrarme",
            style="Auth.Primary.TButton",
            command=self._registrar_usuario,
        ).pack(fill="x", pady=(16, 8))

        ttk.Button(
            self.panel,
            text="Volver al inicio de sesión",
            style="Auth.Secondary.TButton",
            command=self.mostrar_login,
        ).pack(fill="x")

        self.txt_nombre.focus_set()
        self._tarjeta.after_idle(self._actualizar_tarjeta)

    def _iniciar_sesion(self):
        """Verifica las credenciales del usuario."""

        nombre_usuario = self.txt_usuario.get()
        contrasena = self.txt_contrasena.get()

        try:
            usuario = self._servicio.iniciar_sesion(
                nombre_usuario,
                contrasena
            )

            messagebox.showinfo(
                "Bienvenido",
                f"Bienvenido a Social UNA, {usuario.nombre}.",
                parent=self,
            )

            self.unbind("<Return>")
            self.withdraw()

            try:
                self._al_iniciar_sesion(usuario)

            except Exception as error:
                self._servicio.cerrar_sesion()
                self.deiconify()
                self.mostrar_login()

                messagebox.showerror(
                    "Error",
                    f"No fue posible abrir la ventana principal: {error}",
                    parent=self,
                )

        except ErrorAutenticacion as error:
            messagebox.showerror(
                "Error de acceso",
                str(error),
                parent=self,
            )

    def _registrar_usuario(self):
        """Registra una nueva cuenta."""

        nombre = self.txt_nombre.get()
        nombre_usuario = self.txt_usuario_registro.get()
        contrasena = self.txt_contrasena_registro.get()

        try:
            usuario = self._servicio.registrar(
                nombre,
                nombre_usuario,
                contrasena
            )

            messagebox.showinfo(
                "Registro exitoso",
                f"La cuenta de {usuario.nombre} fue creada correctamente."
            )

            self.mostrar_login()
            self.txt_usuario.insert(0, usuario.nombre_usuario)

        except (
            ErrorValidacion,
            ErrorDuplicado,
            ErrorAlmacenamiento
        ) as error:
            messagebox.showerror("No se pudo registrar", str(error))
