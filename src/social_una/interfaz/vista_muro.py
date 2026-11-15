"""
Pantalla del muro de publicaciones, en dos columnas.

A la izquierda están el selector de muro y la caja para publicar; a la derecha,
las publicaciones como tarjetas con scroll. No contiene lógica de negocio:
solo llama al servicio y muestra lo que devuelve.
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from social_una.dominio.errores import ErrorSocialUna
from social_una.dominio.modelos import Publicacion
from social_una.interfaz import alertas
from social_una.interfaz.iconos import cargar_icono
from social_una.servicios.servicio_publicaciones import (
    LARGO_MAXIMO_PUBLICACION,
    ServicioPublicaciones,
)

# Colores y fuente propios de esta pantalla. No se usa ttk.Style para no
# cambiar el aspecto de las pantallas de los otros módulos.
COLOR_FONDO = "#FFFFFF"
COLOR_TARJETA = "#FFFFFF"
COLOR_BORDE = "#CFE0F1"
COLOR_TEXTO = "#102A4C"
COLOR_TEXTO_SUAVE = "#536B87"
COLOR_ACENTO = "#C8102E"
COLOR_ACENTO_OSCURO = "#A90E27"
COLOR_ACENTO_CLARO = "#FBE9ED"
COLOR_AZUL = "#225EA8"
FUENTE = "Segoe UI"
ANCHO_PANEL_IZQUIERDO = 342


class VistaMuro(ttk.Frame):
    """
    Pantalla del muro con dos columnas.

    A la izquierda están el selector de muro y la caja para publicar; a la
    derecha, las publicaciones como tarjetas con scroll.
    """

    def __init__(self, padre: tk.Misc, servicio: ServicioPublicaciones) -> None:
        """Recibe el contenedor y el servicio; no carga datos hasta que se llame a refrescar."""
        super().__init__(padre)
        self._servicio = servicio
        self._modo = tk.StringVar(value="general")
        self._etiquetas_texto: list[tk.Label] = []
        self._botones_modo: dict[str, tk.Radiobutton] = {}
        self._barra_visible = False
        self._ajuste_scroll_programado = None
        self._apilado = False
        self._iconos = {
            "eliminar": cargar_icono(self, "eliminar", 3),
        }
        self._crear_widgets()

    def _crear_widgets(self) -> None:
        """Arma el fondo y las dos columnas de la pantalla."""
        self._fondo = tk.Frame(self, bg=COLOR_FONDO)
        self._fondo.pack(fill="both", expand=True, padx=2, pady=2)
        self._fondo.columnconfigure(0, weight=0)
        self._fondo.columnconfigure(1, weight=1)
        self._fondo.rowconfigure(0, weight=1)
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()
        self._fondo.bind("<Configure>", self._ajustar_columnas)

    def _crear_panel_izquierdo(self) -> None:
        """Crea el selector de muro, la caja para publicar, el contador y el botón."""
        panel = self._panel_izquierdo = tk.Frame(
            self._fondo,
            bg=COLOR_TARJETA,
            width=ANCHO_PANEL_IZQUIERDO,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(8, 6), pady=8)
        panel.grid_propagate(False)

        self._botones_modo.clear()
        for texto, valor in (
            ("Muro general", "general"),
            ("Mi muro", "personal"),
        ):
            boton = tk.Radiobutton(
                panel,
                text=texto,
                value=valor,
                variable=self._modo,
                command=self.refrescar,
                indicatoron=False,
                anchor="w",
                relief="flat",
                bd=0,
                padx=12,
                pady=8,
                font=(FUENTE, 10, "bold"),
                bg=COLOR_TARJETA,
                fg=COLOR_TEXTO,
                selectcolor=COLOR_ACENTO_CLARO,
                activebackground=COLOR_ACENTO_CLARO,
                cursor="hand2",
            )
            boton.pack(fill="x", padx=12, pady=2)
            self._botones_modo[valor] = boton

        tk.Frame(panel, height=1, bg="#DFE8F1").pack(
            fill="x",
            padx=14,
            pady=(12, 14),
        )

        tk.Label(
            panel,
            text="Escribe una publicación",
            font=(FUENTE, 11, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 7))

        self._caja_texto = tk.Text(
            panel,
            height=6,
            width=1,
            wrap="word",
            font=(FUENTE, 10),
            relief="flat",
            bg="#F7F9FC",
            fg=COLOR_TEXTO,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
            highlightcolor=COLOR_AZUL,
            padx=10,
            pady=9,
        )
        self._caja_texto.pack(fill="x", padx=14, pady=4)
        self._caja_texto.bind("<KeyRelease>", self._actualizar_contador)

        estilo = ttk.Style(self)
        estilo.configure(
            "Social.Publish.TButton",
            background=COLOR_AZUL,
            foreground="white",
            font=(FUENTE, 10, "bold"),
            padding=(16, 8),
            borderwidth=0,
        )
        estilo.map(
            "Social.Publish.TButton",
            background=[
                ("pressed", "#164B86"),
                ("active", "#174F8D"),
            ],
        )

        fila = tk.Frame(panel, bg=COLOR_TARJETA)
        fila.pack(fill="x", padx=16, pady=(5, 12))
        self._contador = tk.Label(
            fila,
            text=f"0/{LARGO_MAXIMO_PUBLICACION}",
            font=(FUENTE, 10),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
        )
        self._contador.pack(side="left")
        self._btn_publicar = ttk.Button(
            fila,
            text="Publicar",
            style="Social.Publish.TButton",
            command=self._al_publicar,
        )
        self._btn_publicar.pack(side="right")

    def _crear_panel_derecho(self) -> None:
        """Crea la tarjeta de publicaciones y su scroll solo cuando se requiere."""
        marco = self._panel_derecho = tk.Frame(
            self._fondo,
            bg=COLOR_TARJETA,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        marco.grid(row=0, column=1, sticky="nsew", padx=(6, 8), pady=8)

        self._canvas = tk.Canvas(
            marco, bg=COLOR_TARJETA, highlightthickness=0, bd=0
        )
        self._barra = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=self._canvas.yview,
        )
        self._canvas.configure(yscrollcommand=self._actualizar_barra)
        self._canvas.pack(side="left", fill="both", expand=True)

        self._contenedor = tk.Frame(self._canvas, bg=COLOR_TARJETA)
        self._ventana_contenedor = self._canvas.create_window(
            (0, 0),
            window=self._contenedor,
            anchor="nw",
        )
        self._contenedor.bind("<Configure>", self._al_cambiar_contenedor)
        self._canvas.bind("<Configure>", self._al_cambiar_canvas)

        self._enlazar_rueda(self._canvas)
        self._enlazar_rueda(self._contenedor)

    def _ajustar_columnas(self, evento) -> None:
        """Apila las tarjetas en ventanas estrechas y usa dos columnas en escritorio."""

        apilado = evento.width < 680
        if apilado == self._apilado:
            return

        self._apilado = apilado
        self._fondo.columnconfigure(0, weight=1 if apilado else 0)
        self._fondo.columnconfigure(1, weight=0 if apilado else 1)

        if apilado:
            self._panel_izquierdo.grid_configure(
                row=0,
                column=0,
                sticky="ew",
                padx=8,
                pady=(8, 5),
            )
            self._panel_izquierdo.configure(width=1)
            self._panel_izquierdo.grid_propagate(True)
            self._panel_derecho.grid_configure(
                row=1,
                column=0,
                sticky="nsew",
                padx=8,
                pady=(5, 8),
            )
            self._panel_derecho.configure(height=330)
            self._panel_derecho.grid_propagate(False)
            self._canvas.configure(height=330)
        else:
            self._panel_izquierdo.grid_configure(
                row=0,
                column=0,
                sticky="nsew",
                padx=(8, 6),
                pady=8,
            )
            self._panel_izquierdo.configure(width=ANCHO_PANEL_IZQUIERDO)
            self._panel_izquierdo.grid_propagate(False)
            self._panel_derecho.grid_configure(
                row=0,
                column=1,
                sticky="nsew",
                padx=(6, 8),
                pady=8,
            )
            self._panel_derecho.grid_propagate(True)
            self._canvas.configure(height=1)

        self._fondo.rowconfigure(0, weight=0 if apilado else 1)
        self._fondo.rowconfigure(1, weight=1 if apilado else 0)

    def refrescar(self) -> None:
        """Vuelve a leer el servicio y redibuja las tarjetas; lo llama quien muestre la pantalla."""
        for modo, boton in self._botones_modo.items():
            seleccionado = modo == self._modo.get()
            boton.configure(
                bg=COLOR_ACENTO_CLARO if seleccionado else COLOR_TARJETA,
                fg=COLOR_ACENTO if seleccionado else COLOR_TEXTO,
            )

        try:
            if self._modo.get() == "personal":
                publicaciones = self._servicio.obtener_muro_personal()
            else:
                publicaciones = self._servicio.obtener_muro()
        except ErrorSocialUna as error:
            alertas.mostrar_error(str(error))
            self._limpiar_tarjetas()
            return

        if not publicaciones:
            self._mostrar_mensaje("Todavía no hay publicaciones.")
            self._canvas.yview_moveto(0)
            self._programar_ajuste_scroll()
            return

        self._limpiar_tarjetas()
        for publicacion in publicaciones:
            nombre = self._servicio.obtener_nombre_autor(publicacion.id_autor)
            self._crear_tarjeta(
                publicacion,
                nombre,
                self._formatear_fecha(publicacion.fecha_creacion),
            )
        # Después de redibujar, el scroll vuelve arriba para ver la más reciente
        self._canvas.yview_moveto(0)
        self._programar_ajuste_scroll()

    def _limpiar_tarjetas(self) -> None:
        """Elimina todas las tarjetas que hay en pantalla."""
        for hijo in self._contenedor.winfo_children():
            hijo.destroy()
        self._etiquetas_texto.clear()

    def _mostrar_mensaje(self, texto: str) -> None:
        """Muestra un estado vacío ilustrado dentro de la tarjeta de publicaciones."""
        self._limpiar_tarjetas()
        estado = tk.Frame(self._contenedor, bg=COLOR_TARJETA)
        estado.pack(fill="x", padx=12, pady=(48, 28))
        icono = tk.Canvas(
            estado,
            width=150,
            height=112,
            bg=COLOR_TARJETA,
            highlightthickness=0,
        )
        icono.pack()
        icono.create_rectangle(
            27, 35, 108, 91,
            outline="#6A91B8",
            width=3,
        )
        icono.create_polygon(
            81, 24, 132, 24, 132, 60, 115, 60, 105, 71, 105, 60, 81, 60,
            fill="white",
            outline="#6A91B8",
            width=3,
        )
        for y in (46, 58, 70):
            icono.create_line(39, y, 92, y, fill="#AFC6DD", width=4)
        for x in (94, 106, 118):
            icono.create_oval(x, 38, x + 5, 43, fill="#6A91B8", outline="")

        tk.Label(
            estado,
            text=texto,
            font=(FUENTE, 14, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
        ).pack(pady=(4, 5))
        tk.Label(
            estado,
            text="Sé el primero en compartir algo\ncon la comunidad.",
            font=(FUENTE, 10),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
            justify="center",
        ).pack()

    def _crear_tarjeta(
        self,
        publicacion: Publicacion,
        nombre: str,
        fecha: str,
    ) -> None:
        """Dibuja una tarjeta con la inicial del autor, su nombre, la fecha y el texto."""
        tarjeta = tk.Frame(
            self._contenedor,
            bg=COLOR_TARJETA,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        tarjeta.pack(fill="x", padx=10, pady=(3, 9))

        tk.Frame(tarjeta, bg=COLOR_ACENTO, width=3).pack(
            side="left",
            fill="y",
        )
        contenido = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        contenido.pack(side="left", fill="both", expand=True)

        encabezado = tk.Frame(contenido, bg=COLOR_TARJETA)
        encabezado.pack(fill="x", padx=14, pady=(12, 6))
        avatar = tk.Canvas(
            encabezado,
            width=38,
            height=38,
            bg=COLOR_TARJETA,
            highlightthickness=0,
        )
        avatar.create_oval(3, 3, 35, 35, fill=COLOR_ACENTO_CLARO, outline="")
        avatar.create_text(
            19,
            19,
            text=(nombre[:1].upper() or "?"),
            fill=COLOR_ACENTO,
            font=(FUENTE, 11, "bold"),
        )
        avatar.pack(side="left")

        datos = tk.Frame(encabezado, bg=COLOR_TARJETA)
        datos.pack(side="left", fill="x", expand=True, padx=(9, 0))
        etiqueta_nombre = tk.Label(
            datos,
            text=nombre,
            font=(FUENTE, 10, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            anchor="w",
        )
        etiqueta_nombre.pack(anchor="w")
        etiqueta_fecha = tk.Label(
            datos,
            text=fecha,
            font=(FUENTE, 9),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
            anchor="w",
        )
        etiqueta_fecha.pack(anchor="w")

        if self._servicio.puede_eliminar_publicacion(publicacion):
            tk.Button(
                encabezado,
                text="Eliminar publicación",
                image=self._iconos["eliminar"],
                compound="left",
                command=lambda id_publicacion=publicacion.id_publicacion: (
                    self._al_eliminar_publicacion(id_publicacion)
                ),
                takefocus=True,
                relief="flat",
                borderwidth=0,
                padx=4,
                pady=3,
                bg=COLOR_ACENTO,
                fg="white",
                activebackground=COLOR_ACENTO_OSCURO,
                activeforeground="white",
                font=(FUENTE, 8, "bold"),
                cursor="hand2",
            ).pack(side="right", padx=(8, 0))

        etiqueta_texto = tk.Label(
            contenido,
            text=publicacion.texto,
            font=(FUENTE, 10),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            justify="left",
            anchor="w",
            wraplength=self._ancho_texto(),
        )
        etiqueta_texto.pack(fill="x", padx=14, pady=(0, 14))
        self._etiquetas_texto.append(etiqueta_texto)

        for widget in (
            tarjeta,
            contenido,
            encabezado,
            avatar,
            datos,
            etiqueta_nombre,
            etiqueta_fecha,
            etiqueta_texto,
        ):
            self._enlazar_rueda(widget)

    def _al_eliminar_publicacion(self, id_publicacion: int) -> None:
        """Confirma y elimina una publicación propia."""
        if not alertas.confirmar(
            "¿Deseas eliminar esta publicación? Esta acción no se puede deshacer."
        ):
            return

        try:
            self._servicio.eliminar_publicacion(id_publicacion)
        except ErrorSocialUna as error:
            alertas.mostrar_error(str(error))
            self.refrescar()
            return

        alertas.mostrar_informacion("La publicación se eliminó correctamente.")
        self.refrescar()

    def _ancho_texto(self) -> int:
        """Devuelve el ancho disponible para el texto de una tarjeta."""
        return max(self._canvas.winfo_width() - 70, 150)

    def _al_cambiar_contenedor(self, evento) -> None:
        """Ajusta el área desplazable al tamaño real de las publicaciones."""
        if evento.widget is not self._contenedor:
            return
        caja = self._canvas.bbox("all")
        if caja is not None:
            self._canvas.configure(scrollregion=caja)
        self._programar_ajuste_scroll()

    def _al_cambiar_canvas(self, evento) -> None:
        """Ajusta el ancho del contenido y sus textos al cambiar la ventana."""
        self._canvas.itemconfigure(
            self._ventana_contenedor,
            width=max(evento.width, 1),
        )
        for etiqueta in self._etiquetas_texto:
            etiqueta.configure(wraplength=max(evento.width - 70, 150))
        self._programar_ajuste_scroll()

    def _programar_ajuste_scroll(self) -> None:
        """Agrupa reajustes del lienzo tras cambios de tamaño o contenido."""
        if self._ajuste_scroll_programado is None:
            self._ajuste_scroll_programado = self.after_idle(
                self._ajustar_scroll
            )

    def _ajustar_scroll(self) -> None:
        """Muestra la barra solo cuando las publicaciones exceden el panel."""
        self._ajuste_scroll_programado = None
        if not self._canvas.winfo_exists():
            return

        caja = self._canvas.bbox("all")
        alto_contenido = 0 if caja is None else caja[3] - caja[1]
        necesita_barra = alto_contenido > self._canvas.winfo_height() + 2
        if necesita_barra == self._barra_visible:
            return

        self._barra_visible = necesita_barra
        if necesita_barra:
            self._barra.pack(side="right", fill="y")
        else:
            self._barra.pack_forget()
        self._programar_ajuste_scroll()

    def _actualizar_barra(self, inicio: str, fin: str) -> None:
        """Actualiza el indicador de la barra y su visibilidad."""
        self._barra.set(inicio, fin)
        self._programar_ajuste_scroll()

    def _enlazar_rueda(self, widget: tk.Misc) -> None:
        """Hace que la rueda del mouse sobre este widget mueva el scroll del muro."""
        widget.bind("<MouseWheel>", self._al_girar_rueda)

    def _al_girar_rueda(self, evento) -> None:
        """Desplaza el muro si hay publicaciones fuera del área visible."""
        if self._barra_visible:
            self._canvas.yview_scroll(int(-evento.delta / 120), "units")

    def _al_publicar(self) -> None:
        """Envía el texto escrito al servicio y, si se publica, vacía la caja y redibuja."""
        texto = self._caja_texto.get("1.0", "end-1c")
        try:
            self._servicio.publicar(texto)
        except ErrorSocialUna as error:
            alertas.mostrar_error(str(error))
            return
        self._caja_texto.delete("1.0", "end")
        self._actualizar_contador()
        self.refrescar()

    def _actualizar_contador(self, evento=None) -> None:
        """Muestra cuántos caracteres lleva escritos la caja, sobre el máximo permitido."""
        if evento is not None and evento.widget is not self._caja_texto:
            return
        cantidad = len(self._caja_texto.get("1.0", "end-1c"))
        self._contador.configure(text=f"{cantidad}/{LARGO_MAXIMO_PUBLICACION}")

    @staticmethod
    def _formatear_fecha(fecha_iso: str) -> str:
        """Convierte una fecha ISO 8601 a la hora local, con formato día/mes/año hora:minutos."""
        try:
            return datetime.fromisoformat(fecha_iso).astimezone().strftime(
                "%d/%m/%Y %H:%M"
            )
        except ValueError:
            return fecha_iso