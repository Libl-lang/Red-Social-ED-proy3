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
from social_una.interfaz import alertas
from social_una.servicios.servicio_publicaciones import (
    LARGO_MAXIMO_PUBLICACION,
    ServicioPublicaciones,
)

# Colores y fuente propios de esta pantalla. No se usa ttk.Style para no
# cambiar el aspecto de las pantallas de los otros módulos.
COLOR_FONDO = "#F0F2F5"
COLOR_TARJETA = "#FFFFFF"
COLOR_BORDE = "#DADDE1"
COLOR_TEXTO = "#1C1E21"
COLOR_TEXTO_SUAVE = "#65676B"
COLOR_ACENTO = "#B5121B"
COLOR_ACENTO_OSCURO = "#8E0E15"
COLOR_ACENTO_CLARO = "#FBE9EA"
FUENTE = "Segoe UI"
ANCHO_PANEL_IZQUIERDO = 340


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
        # Se guardan las etiquetas de texto para reacomodar su ancho al cambiar el tamaño
        self._etiquetas_texto: list[tk.Label] = []
        self._crear_widgets()

    def _crear_widgets(self) -> None:
        """Arma el fondo y las dos columnas de la pantalla."""
        self._fondo = tk.Frame(self, bg=COLOR_FONDO)
        self._fondo.pack(fill="both", expand=True)
        # La columna izquierda mantiene su ancho; la derecha se estira con la ventana
        self._fondo.columnconfigure(0, weight=0)
        self._fondo.columnconfigure(1, weight=1)
        self._fondo.rowconfigure(0, weight=1)
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()

    def _crear_panel_izquierdo(self) -> None:
        """Crea el selector de muro, la caja para publicar, el contador y el botón."""
        panel = tk.Frame(
            self._fondo,
            bg=COLOR_TARJETA,
            width=ANCHO_PANEL_IZQUIERDO,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        panel.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        # Evita que el panel se encoja al tamaño de su contenido
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text="Publicaciones",
            font=(FUENTE, 13, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(14, 8))

        for texto, valor in (("Muro general", "general"), ("Mi muro", "personal")):
            tk.Radiobutton(
                panel,
                text=texto,
                value=valor,
                variable=self._modo,
                command=self.refrescar,
                indicatoron=False,
                anchor="w",
                relief="flat",
                bd=0,
                padx=10,
                pady=6,
                font=(FUENTE, 10),
                bg=COLOR_TARJETA,
                fg=COLOR_TEXTO,
                selectcolor=COLOR_ACENTO_CLARO,
                activebackground=COLOR_ACENTO_CLARO,
                cursor="hand2",
            ).pack(fill="x", padx=8, pady=1)

        # Línea separadora entre el selector y la caja para publicar
        tk.Frame(panel, height=1, bg=COLOR_BORDE).pack(fill="x", padx=12, pady=10)

        tk.Label(
            panel,
            text="Escribe una publicación",
            font=(FUENTE, 10, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            anchor="w",
        ).pack(fill="x", padx=12)

        self._caja_texto = tk.Text(
            panel,
            height=7,
            width=1,
            wrap="word",
            font=(FUENTE, 10),
            relief="flat",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
            highlightcolor=COLOR_ACENTO,
            padx=8,
            pady=6,
        )
        self._caja_texto.pack(fill="x", padx=12, pady=4)
        self._caja_texto.bind("<KeyRelease>", self._actualizar_contador)

        fila = tk.Frame(panel, bg=COLOR_TARJETA)
        fila.pack(fill="x", padx=12, pady=(4, 12))
        self._contador = tk.Label(
            fila,
            text=f"0/{LARGO_MAXIMO_PUBLICACION}",
            font=(FUENTE, 9),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
        )
        self._contador.pack(side="left")
        tk.Button(
            fila,
            text="Publicar",
            command=self._al_publicar,
            bg=COLOR_ACENTO,
            fg="white",
            activebackground=COLOR_ACENTO_OSCURO,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=4,
            cursor="hand2",
            font=(FUENTE, 10, "bold"),
        ).pack(side="right")

    def _crear_panel_derecho(self) -> None:
        """Crea la zona de tarjetas con scroll vertical."""
        marco = tk.Frame(self._fondo, bg=COLOR_FONDO)
        marco.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        self._canvas = tk.Canvas(marco, bg=COLOR_FONDO, highlightthickness=0)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # Un lienzo no hace scroll de widgets directamente: se mete un Frame
        # dentro del lienzo y las tarjetas van dentro de ese Frame
        self._contenedor = tk.Frame(self._canvas, bg=COLOR_FONDO)
        self._ventana_contenedor = self._canvas.create_window(
            (0, 0), window=self._contenedor, anchor="nw"
        )
        self._contenedor.bind("<Configure>", self._al_cambiar_contenedor)
        self._canvas.bind("<Configure>", self._al_cambiar_canvas)

        self._enlazar_rueda(self._canvas)
        self._enlazar_rueda(self._contenedor)

    def refrescar(self) -> None:
        """Vuelve a leer el servicio y redibuja las tarjetas; lo llama quien muestre la pantalla."""
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
            return

        self._limpiar_tarjetas()
        for publicacion in publicaciones:
            nombre = self._servicio.obtener_nombre_autor(publicacion.id_autor)
            self._crear_tarjeta(
                nombre,
                self._formatear_fecha(publicacion.fecha_creacion),
                publicacion.texto,
            )
        # Después de redibujar, el scroll vuelve arriba para ver la más reciente
        self._canvas.yview_moveto(0)

    def _limpiar_tarjetas(self) -> None:
        """Elimina todas las tarjetas que hay en pantalla."""
        for hijo in self._contenedor.winfo_children():
            hijo.destroy()
        self._etiquetas_texto.clear()

    def _mostrar_mensaje(self, texto: str) -> None:
        """Reemplaza las tarjetas por un mensaje centrado."""
        self._limpiar_tarjetas()
        tk.Label(
            self._contenedor,
            text=texto,
            font=(FUENTE, 11),
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SUAVE,
        ).pack(pady=30)

    def _crear_tarjeta(self, nombre: str, fecha: str, texto: str) -> None:
        """Dibuja una tarjeta con la inicial del autor, su nombre, la fecha y el texto."""
        tarjeta = tk.Frame(
            self._contenedor,
            bg=COLOR_TARJETA,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        tarjeta.pack(fill="x", padx=4, pady=(0, 8))

        encabezado = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        encabezado.pack(fill="x", padx=12, pady=(10, 4))

        # Círculo con la inicial del autor, a modo de foto de perfil
        avatar = tk.Canvas(
            encabezado, width=34, height=34, bg=COLOR_TARJETA, highlightthickness=0
        )
        avatar.create_oval(2, 2, 32, 32, fill=COLOR_ACENTO_CLARO, outline="")
        avatar.create_text(
            17,
            17,
            text=(nombre[:1].upper() or "?"),
            fill=COLOR_ACENTO,
            font=(FUENTE, 11, "bold"),
        )
        avatar.pack(side="left")

        datos = tk.Frame(encabezado, bg=COLOR_TARJETA)
        datos.pack(side="left", padx=(8, 0))
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

        etiqueta_texto = tk.Label(
            tarjeta,
            text=texto,
            font=(FUENTE, 10),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            justify="left",
            anchor="w",
            wraplength=self._ancho_texto(),
        )
        etiqueta_texto.pack(fill="x", padx=12, pady=(0, 12))
        self._etiquetas_texto.append(etiqueta_texto)

        # Cada widget captura la rueda del mouse por separado, así que hay que
        # enlazarla en todos para que el scroll funcione sobre las tarjetas
        for widget in (
            tarjeta,
            encabezado,
            avatar,
            datos,
            etiqueta_nombre,
            etiqueta_fecha,
            etiqueta_texto,
        ):
            self._enlazar_rueda(widget)

    def _ancho_texto(self) -> int:
        """Devuelve el ancho disponible para el texto de una tarjeta, con un mínimo de 150."""
        return max(self._canvas.winfo_width() - 60, 150)

    def _al_cambiar_contenedor(self, evento) -> None:
        """Ajusta el área de scroll al tamaño real del contenido."""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _al_cambiar_canvas(self, evento) -> None:
        """Estira las tarjetas al ancho de la ventana y reacomoda el texto."""
        self._canvas.itemconfigure(self._ventana_contenedor, width=evento.width)
        for etiqueta in self._etiquetas_texto:
            etiqueta.configure(wraplength=max(evento.width - 60, 150))

    def _enlazar_rueda(self, widget: tk.Misc) -> None:
        """Hace que la rueda del mouse sobre este widget mueva el scroll del muro."""
        widget.bind("<MouseWheel>", self._al_girar_rueda)

    def _al_girar_rueda(self, evento) -> None:
        """Desplaza el muro hacia arriba o abajo según el giro de la rueda."""
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