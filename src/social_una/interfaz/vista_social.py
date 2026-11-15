"""
Vista social de Social UNA (Modulo 2).

Permite buscar usuarios, consultar si ya son amigos,
agregar amigos y visualizar la lista de amistades.
"""

import tkinter as tk
from tkinter import ttk

from social_una.dominio.errores import ErrorSocialUna
from social_una.dominio.modelos import Usuario
from social_una.interfaz.alertas import (
    mostrar_error,
    mostrar_informacion,
)
from social_una.servicios.servicio_social import ServicioSocial


COLOR_MARINO = "#102A4C"
COLOR_AZUL = "#225EA8"
COLOR_ROJO = "#C8102E"
COLOR_FONDO = "#F3F6FA"
COLOR_BORDE = "#CFE0F1"
COLOR_TEXTO_SUAVE = "#536B87"
COLOR_AVATAR_AZUL = "#D9EAFB"
COLOR_AVATAR_ROJO = "#FBE1E5"
FUENTE = "Segoe UI"


def _dibujar_persona(
    lienzo: tk.Canvas,
    centro_x: float,
    centro_y: float,
    escala: float,
    color: str,
) -> None:
    """Dibuja una silueta simétrica con cabeza circular y hombros."""
    radio = 4.2 * escala
    cabeza_y = centro_y - 7 * escala
    lienzo.create_oval(
        centro_x - radio,
        cabeza_y - radio,
        centro_x + radio,
        cabeza_y + radio,
        fill=color,
        outline="",
    )
    puntos_cuerpo = (
        centro_x - 3 * escala, centro_y - 3 * escala,
        centro_x - 3 * escala, centro_y,
        centro_x - 7 * escala, centro_y + escala,
        centro_x - 10 * escala, centro_y + 4 * escala,
        centro_x - 12 * escala, centro_y + 8 * escala,
        centro_x - 12 * escala, centro_y + 14 * escala,
        centro_x + 12 * escala, centro_y + 14 * escala,
        centro_x + 12 * escala, centro_y + 8 * escala,
        centro_x + 10 * escala, centro_y + 4 * escala,
        centro_x + 7 * escala, centro_y + escala,
        centro_x + 3 * escala, centro_y,
        centro_x + 3 * escala, centro_y - 3 * escala,
    )
    lienzo.create_polygon(
        *puntos_cuerpo,
        fill=color,
        outline="",
    )


def _dibujar_grupo(
    lienzo: tk.Canvas,
    ancho: int,
    alto: int,
    color: str,
) -> None:
    escala = min((ancho - 4) / 52, (alto - 4) / 26)
    centro_x = ancho / 2
    centro_y = alto / 2
    for desplazamiento in (-14, 14):
        _dibujar_persona(
            lienzo,
            centro_x + desplazamiento * escala,
            centro_y,
            escala,
            color,
        )


class _PanelDesplazable(tk.Frame):
    """Panel blanco con desplazamiento vertical solo cuando hace falta."""

    def __init__(self, padre: tk.Misc) -> None:
        super().__init__(
            padre,
            bg="white",
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        self._ajuste_programado = None

        self.canvas = tk.Canvas(
            self,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        self.barra = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self._actualizar_barra)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.contenido = tk.Frame(self.canvas, bg="white")
        self._ventana = self.canvas.create_window(
            (0, 0),
            window=self.contenido,
            anchor="nw",
        )
        self.contenido.bind("<Configure>", self._programar_ajuste)
        self.canvas.bind("<Configure>", self._al_redimensionar)

    def _al_redimensionar(self, evento: tk.Event) -> None:
        self.canvas.itemconfigure(self._ventana, width=max(evento.width, 1))
        self._programar_ajuste()

    def _actualizar_barra(self, inicio: str, fin: str) -> None:
        self.barra.set(inicio, fin)

    def _programar_ajuste(self, _evento=None) -> None:
        if _evento is not None and not self.winfo_exists():
            return
        if self._ajuste_programado is None:
            self._ajuste_programado = self.after_idle(self._ajustar)

    def _ajustar(self) -> None:
        self._ajuste_programado = None
        if not self.winfo_exists():
            return

        self.contenido.update_idletasks()
        alto_contenido = self.contenido.winfo_reqheight()
        alto_visible = self.canvas.winfo_height()
        necesita_barra = alto_contenido > alto_visible + 2
        barra_visible = self.barra.winfo_manager() == "pack"

        if necesita_barra != barra_visible:
            if necesita_barra:
                self.barra.pack(side="right", fill="y")
            else:
                self.barra.pack_forget()
            self._programar_ajuste()
            return

        ancho = max(self.canvas.winfo_width(), 1)
        alto = max(alto_visible, alto_contenido)
        self.canvas.itemconfigure(self._ventana, height=alto)
        self.canvas.configure(
            scrollregion=(0, 0, ancho, alto)
        )


class VistaSocial(ttk.Frame):
    """Interfaz para las operaciones sociales del usuario activo."""

    def __init__(
        self,
        padre: tk.Misc,
        servicio: ServicioSocial,
    ) -> None:
        super().__init__(padre)

        self._servicio = servicio
        self._resultados = {}
        self._amigos = []

        self._crear_interfaz()
        self._mostrar_resultados("")
        self._refrescar_amigos()

    def _crear_interfaz(self) -> None:
        """Construye el encabezado, búsqueda y paneles adaptables."""

        estilo = ttk.Style(self)
        estilo.configure(
            "SocialFriends.Search.TEntry",
            fieldbackground="#F8FAFC",
            foreground=COLOR_MARINO,
            padding=(12, 9),
            bordercolor=COLOR_BORDE,
            lightcolor=COLOR_BORDE,
            darkcolor=COLOR_BORDE,
        )
        estilo.configure(
            "SocialFriends.Primary.TButton",
            background=COLOR_AZUL,
            foreground="white",
            font=(FUENTE, 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        estilo.map(
            "SocialFriends.Primary.TButton",
            background=[
                ("pressed", "#164B86"),
                ("active", "#174F8D"),
            ],
        )
        estilo.configure(
            "SocialFriends.Subtle.TButton",
            background="white",
            foreground=COLOR_TEXTO_SUAVE,
            font=(FUENTE, 9),
            padding=(8, 7),
            borderwidth=0,
        )

        self.configure(style="TFrame")
        self._contenedor_principal = tk.Frame(self, bg=COLOR_FONDO)
        self._contenedor_principal.pack(fill="both", expand=True, padx=2, pady=2)

        self._apilado = False
        self._crear_encabezado()
        self._crear_barra_busqueda()

        self._cuerpo_paneles = tk.Frame(
            self._contenedor_principal,
            bg=COLOR_FONDO,
        )
        self._cuerpo_paneles.pack(fill="both", expand=True, pady=(14, 0))
        self._cuerpo_paneles.columnconfigure(0, weight=1)
        self._cuerpo_paneles.columnconfigure(1, weight=1)
        self._cuerpo_paneles.rowconfigure(0, weight=1)

        self._panel_resultados = self._crear_panel(
            self._cuerpo_paneles,
            "Resultados de búsqueda",
            "buscar",
        )
        self._panel_amigos = self._crear_panel(
            self._cuerpo_paneles,
            "Mis amistades",
            "amistades",
        )
        self._panel_resultados.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )
        self._panel_amigos.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )

        self._etiqueta_estado = tk.Label(
            self._contenedor_principal,
            text="",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w",
        )
        self._etiqueta_estado.pack(fill="x", pady=(6, 0))

        self._crear_almacen_compatibilidad()
        self.bind("<Configure>", self._ajustar_distribucion)

    def _crear_encabezado(self) -> None:
        encabezado = tk.Frame(
            self._contenedor_principal,
            bg="white",
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        encabezado.pack(fill="x")
        tk.Frame(encabezado, bg=COLOR_ROJO, width=5).pack(
            side="left",
            fill="y",
        )

        icono = tk.Canvas(
            encabezado,
            width=66,
            height=68,
            bg="white",
            highlightthickness=0,
        )
        icono.pack(side="left", padx=(12, 4), pady=8)
        _dibujar_grupo(icono, 66, 68, COLOR_ROJO)

        texto = tk.Frame(encabezado, bg="white")
        texto.pack(side="left", fill="both", expand=True, pady=12)
        tk.Label(
            texto,
            text="Amistades y búsqueda",
            bg="white",
            fg=COLOR_MARINO,
            font=(FUENTE, 18, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            texto,
            text="Encontrá estudiantes y conectá con tus compañeros",
            bg="white",
            fg=COLOR_TEXTO_SUAVE,
            font=(FUENTE, 10),
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

    def _crear_barra_busqueda(self) -> None:
        marco = tk.Frame(
            self._contenedor_principal,
            bg="white",
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        marco.pack(fill="x", pady=(12, 0))

        campo = tk.Frame(marco, bg="#F8FAFC")
        campo.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(12, 8),
            pady=9,
        )
        icono_busqueda = tk.Canvas(
            campo,
            width=22,
            height=22,
            bg="#F8FAFC",
            highlightthickness=0,
        )
        icono_busqueda.pack(side="left", padx=(8, 4))
        icono_busqueda.create_oval(
            3, 3, 14, 14,
            outline=COLOR_TEXTO_SUAVE,
            width=2,
        )
        icono_busqueda.create_line(
            13, 13, 19, 19,
            fill=COLOR_TEXTO_SUAVE,
            width=2,
        )

        self._entrada_busqueda = ttk.Entry(
            campo,
            style="SocialFriends.Search.TEntry",
        )
        self._entrada_busqueda.pack(side="left", fill="x", expand=True)
        self._entrada_busqueda.bind("<KeyRelease>", self._on_buscar)
        self._entrada_busqueda.bind("<Return>", self._buscar_manual)

        ttk.Button(
            marco,
            text="Buscar",
            style="SocialFriends.Primary.TButton",
            command=self._buscar_manual,
        ).pack(side="right", padx=(0, 12), pady=9)
        ttk.Button(
            marco,
            text="Limpiar",
            style="SocialFriends.Subtle.TButton",
            command=self._limpiar_busqueda,
        ).pack(side="right", padx=(0, 6), pady=9)

    def _crear_panel(
        self,
        padre: tk.Misc,
        titulo: str,
        tipo: str,
    ) -> _PanelDesplazable:
        panel = _PanelDesplazable(padre)
        cabecera = tk.Frame(panel.contenido, bg="white")
        cabecera.pack(fill="x", padx=14, pady=(12, 0))

        icono = tk.Canvas(
            cabecera,
            width=34,
            height=34,
            bg="white",
            highlightthickness=0,
        )
        icono.pack(side="left", padx=(0, 8))
        if tipo == "buscar":
            icono.create_oval(5, 5, 23, 23, outline=COLOR_ROJO, width=2)
            icono.create_line(20, 20, 29, 29, fill=COLOR_ROJO, width=3)
        else:
            _dibujar_grupo(icono, 34, 34, COLOR_ROJO)

        tk.Label(
            cabecera,
            text=titulo,
            bg="white",
            fg=COLOR_MARINO,
            font=(FUENTE, 14, "bold"),
            anchor="w",
        ).pack(side="left", anchor="center")
        if tipo == "amistades":
            self._btn_actualizar_amigos = ttk.Button(
                cabecera,
                text="Actualizar",
                style="SocialFriends.Subtle.TButton",
                command=self._refrescar_amigos,
            )
            self._btn_actualizar_amigos.pack(side="right")

        tk.Frame(panel.contenido, bg="#D8E3EF", height=1).pack(
            fill="x",
            padx=14,
            pady=(8, 0),
        )
        acento = tk.Frame(panel.contenido, bg=COLOR_ROJO, height=4, width=68)
        acento.pack(anchor="w", padx=14)

        filas = tk.Frame(panel.contenido, bg="white")
        filas.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        if tipo == "buscar":
            self._filas_resultados = filas
        else:
            self._filas_amigos = filas
        return panel

    def _crear_almacen_compatibilidad(self) -> None:
        """Conserva las estructuras de selección utilizadas por integraciones previas."""
        self._lista_resultados = ttk.Treeview(
            self,
            columns=("nombre", "usuario", "estado"),
            show="headings",
            selectmode="browse",
        )
        self._lista_amigos = tk.Listbox(self, height=1)

    def _ajustar_distribucion(self, evento: tk.Event) -> None:
        """Pasa a columnas apiladas cuando el contenido queda estrecho."""
        if evento.widget is not self:
            return

        apilado = evento.width < 760
        if apilado == self._apilado:
            return
        self._apilado = apilado

        if apilado:
            self._cuerpo_paneles.columnconfigure(0, weight=1)
            self._cuerpo_paneles.columnconfigure(1, weight=0)
            self._panel_resultados.grid_configure(
                row=0,
                column=0,
                sticky="nsew",
                padx=0,
                pady=(0, 8),
            )
            self._panel_resultados.configure(height=270)
            self._panel_resultados.grid_propagate(False)
            self._panel_amigos.grid_configure(
                row=1,
                column=0,
                sticky="nsew",
                padx=0,
                pady=(8, 0),
            )
            self._panel_amigos.configure(height=270)
            self._panel_amigos.grid_propagate(False)
            self._cuerpo_paneles.rowconfigure(0, weight=0)
            self._cuerpo_paneles.rowconfigure(1, weight=0)
        else:
            self._cuerpo_paneles.columnconfigure(0, weight=1)
            self._cuerpo_paneles.columnconfigure(1, weight=1)
            self._panel_resultados.grid_configure(
                row=0,
                column=0,
                sticky="nsew",
                padx=(0, 8),
                pady=0,
            )
            self._panel_resultados.grid_propagate(True)
            self._panel_amigos.grid_configure(
                row=0,
                column=1,
                sticky="nsew",
                padx=(8, 0),
                pady=0,
            )
            self._panel_amigos.grid_propagate(True)
            self._cuerpo_paneles.rowconfigure(0, weight=1)
            self._cuerpo_paneles.rowconfigure(1, weight=0)

    @staticmethod
    def _iniciales(nombre: str) -> str:
        partes = nombre.split()
        if not partes:
            return "?"
        return "".join(parte[0] for parte in partes[:2]).upper()

    def _crear_avatar(self, padre: tk.Misc, usuario: Usuario) -> tk.Canvas:
        color = (
            COLOR_AVATAR_AZUL
            if usuario.id_usuario % 2
            else COLOR_AVATAR_ROJO
        )
        avatar = tk.Canvas(
            padre,
            width=50,
            height=50,
            bg="white",
            highlightthickness=0,
        )
        avatar.create_oval(2, 2, 48, 48, fill=color, outline="")
        avatar.create_text(
            25,
            25,
            text=self._iniciales(usuario.nombre),
            fill=COLOR_MARINO,
            font=(FUENTE, 11, "bold"),
        )
        return avatar

    @staticmethod
    def _limpiar_filas(contenedor: tk.Misc) -> None:
        for widget in contenedor.winfo_children():
            widget.destroy()

    def _mostrar_estado_vacio(
        self,
        contenedor: tk.Misc,
        mensaje: str,
    ) -> None:
        tk.Label(
            contenedor,
            text=mensaje,
            bg="white",
            fg=COLOR_TEXTO_SUAVE,
            font=(FUENTE, 10),
            justify="center",
            wraplength=310,
        ).pack(fill="x", padx=12, pady=32)

    def _crear_fila_usuario(
        self,
        contenedor: tk.Misc,
        usuario: Usuario,
        es_amigo: bool,
    ) -> None:
        fila = tk.Frame(contenedor, bg="white")
        fila.pack(fill="x", padx=8)
        fila.grid_columnconfigure(1, weight=1)

        self._crear_avatar(fila, usuario).grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(8, 12),
            pady=8,
        )
        tk.Label(
            fila,
            text=usuario.nombre,
            bg="white",
            fg=COLOR_MARINO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=0, column=1, sticky="sw", pady=(8, 0))
        tk.Label(
            fila,
            text=f"@{usuario.nombre_usuario}",
            bg="white",
            fg=COLOR_TEXTO_SUAVE,
            font=(FUENTE, 9),
            anchor="w",
        ).grid(row=1, column=1, sticky="nw", pady=(0, 8))

        if es_amigo:
            tk.Label(
                fila,
                text="Amigo",
                bg="#F1F5F9",
                fg=COLOR_TEXTO_SUAVE,
                font=(FUENTE, 9, "bold"),
                padx=10,
                pady=6,
            ).grid(row=0, column=2, rowspan=2, padx=(8, 4))
        else:
            ttk.Button(
                fila,
                text="Agregar",
                style="SocialFriends.Primary.TButton",
                command=lambda id_usuario=usuario.id_usuario: (
                    self._seleccionar_y_agregar(id_usuario)
                ),
            ).grid(row=0, column=2, rowspan=2, padx=(8, 4))

        tk.Frame(contenedor, bg="#D8E3EF", height=1).pack(
            fill="x",
            padx=14,
        )

    def _seleccionar_y_agregar(self, id_usuario: int) -> None:
        iid = str(id_usuario)
        if self._lista_resultados.exists(iid):
            self._lista_resultados.selection_set(iid)
        self._agregar_amigo_seleccionado()

    # --------------------------------------------------
    # Búsqueda de usuarios
    # --------------------------------------------------

    def _on_buscar(self, event: tk.Event) -> None:
        """Actualiza los resultados mientras se escribe."""

        if event.widget is not self._entrada_busqueda:
            return
        self._mostrar_resultados(
            self._entrada_busqueda.get()
        )

    def _buscar_manual(self, event=None) -> None:
        """Ejecuta la búsqueda mediante el botón o Enter."""

        if event is not None and event.widget is not self._entrada_busqueda:
            return
        self._mostrar_resultados(
            self._entrada_busqueda.get()
        )

    def _limpiar_busqueda(self) -> None:
        """Limpia el texto y vuelve a mostrar los usuarios."""

        self._entrada_busqueda.delete(0, tk.END)
        self._mostrar_resultados("")

    def _mostrar_resultados(self, texto: str) -> None:
        """Consulta el servicio y muestra los usuarios encontrados."""

        for item in self._lista_resultados.get_children():
            self._lista_resultados.delete(item)
        self._resultados.clear()
        self._limpiar_filas(self._filas_resultados)
        self._panel_resultados._programar_ajuste()

        try:
            resultados = self._servicio.buscar_usuarios(texto)

        except ErrorSocialUna as error:
            mostrar_error(str(error))
            self._etiqueta_estado.config(
                text="No fue posible realizar la búsqueda."
            )
            return

        if not resultados:
            self._mostrar_estado_vacio(
                self._filas_resultados,
                "No encontramos estudiantes con esa búsqueda.",
            )

        for resultado in resultados:
            usuario: Usuario = resultado["usuario"]
            es_amigo: bool = resultado["es_amigo"]
            self._resultados[usuario.id_usuario] = usuario

            estado = (
                "Ya es amigo"
                if es_amigo
                else "No es amigo"
            )

            self._lista_resultados.insert(
                "",
                tk.END,
                iid=str(usuario.id_usuario),
                values=(
                    usuario.nombre,
                    usuario.nombre_usuario,
                    estado,
                ),
            )
            self._crear_fila_usuario(
                self._filas_resultados,
                usuario,
                es_amigo,
            )

        self._etiqueta_estado.config(
            text=f"Resultados encontrados: {len(resultados)}"
        )

    # --------------------------------------------------
    # Agregar amigos
    # --------------------------------------------------

    def _agregar_amigo_seleccionado(self) -> None:
        """Agrega como amigo a la persona seleccionada."""

        seleccion = self._lista_resultados.selection()

        if not seleccion:
            mostrar_error(
                "Selecciona una persona de los resultados."
            )
            return

        id_amigo = int(seleccion[0])

        valores = self._lista_resultados.item(
            seleccion[0],
            "values",
        )

        if valores and valores[2] == "Ya es amigo":
            mostrar_informacion(
                "Esta persona ya forma parte de tu lista de amigos."
            )
            return

        try:
            self._servicio.agregar_amigo(id_amigo)

        except ErrorSocialUna as error:
            mostrar_error(str(error))
            return

        mostrar_informacion(
            "La persona se agregó correctamente a tu lista de amigos."
        )

        self._mostrar_resultados(
            self._entrada_busqueda.get()
        )
        self._refrescar_amigos()

    # --------------------------------------------------
    # Lista de amigos
    # --------------------------------------------------

    def _refrescar_amigos(self) -> None:
        """Actualiza la lista de amigos del usuario activo."""

        self._lista_amigos.delete(0, tk.END)
        self._amigos.clear()
        self._limpiar_filas(self._filas_amigos)
        self._panel_amigos._programar_ajuste()

        try:
            amigos = self._servicio.listar_mis_amigos()

        except ErrorSocialUna as error:
            mostrar_error(str(error))
            self._etiqueta_estado.config(
                text="No fue posible cargar la lista de amigos."
            )
            return

        self._amigos.extend(amigos)
        if not amigos:
            self._mostrar_estado_vacio(
                self._filas_amigos,
                "Todavía no tienes amistades. Busca estudiantes para conectar.",
            )

        for usuario in amigos:
            self._lista_amigos.insert(
                tk.END,
                f"{usuario.nombre} (@{usuario.nombre_usuario})",
            )
            fila = tk.Frame(self._filas_amigos, bg="white")
            fila.pack(fill="x", padx=8)
            self._crear_avatar(fila, usuario).grid(
                row=0,
                column=0,
                rowspan=2,
                padx=(8, 12),
                pady=8,
            )
            tk.Label(
                fila,
                text=usuario.nombre,
                bg="white",
                fg=COLOR_MARINO,
                font=(FUENTE, 10, "bold"),
                anchor="w",
            ).grid(row=0, column=1, sticky="sw", pady=(8, 0))
            tk.Label(
                fila,
                text=f"@{usuario.nombre_usuario}",
                bg="white",
                fg=COLOR_TEXTO_SUAVE,
                font=(FUENTE, 9),
                anchor="w",
            ).grid(row=1, column=1, sticky="nw", pady=(0, 8))
            fila.grid_columnconfigure(1, weight=1)
            icono_amigos = tk.Canvas(
                fila,
                width=30,
                height=30,
                bg="white",
                highlightthickness=0,
            )
            icono_amigos.grid(row=0, column=2, rowspan=2, padx=(8, 6))
            _dibujar_persona(
                icono_amigos,
                15,
                14,
                0.9,
                COLOR_ROJO,
            )
            tk.Frame(self._filas_amigos, bg="#D8E3EF", height=1).pack(
                fill="x",
                padx=14,
            )

        self._etiqueta_estado.config(
            text=(
                f"Tu lista de amigos contiene "
                f"{len(amigos)} personas."
            )
        )

    # --------------------------------------------------
    # API pública
    # --------------------------------------------------

    def refrescar(self) -> None:
        """Refresca los resultados de búsqueda y la lista de amigos.

        Este método se invoca desde la ventana principal cada vez que el
        usuario selecciona la pestaña de amistades, para asegurar que los
        datos se muestran actualizados.
        """
        self._mostrar_resultados("")
        self._refrescar_amigos()
