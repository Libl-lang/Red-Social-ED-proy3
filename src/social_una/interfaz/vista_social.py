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


class VistaSocial(ttk.Frame):
    """Interfaz para las operaciones sociales del usuario activo."""

    def __init__(
        self,
        padre: tk.Misc,
        servicio: ServicioSocial,
    ) -> None:
        super().__init__(padre)

        self._servicio = servicio

        self._crear_interfaz()
        self._mostrar_resultados("")
        self._refrescar_amigos()

    def _crear_interfaz(self) -> None:
        """Construye los paneles de búsqueda, resultados y amistades."""

        # Panel superior: búsqueda.
        frame_buscar = ttk.LabelFrame(
            self,
            text="Buscar personas",
            padding=10,
        )
        frame_buscar.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(
            frame_buscar,
            text="Nombre o nombre de usuario:",
        ).pack(side=tk.LEFT)

        self._entrada_busqueda = ttk.Entry(
            frame_buscar,
            width=35,
        )
        self._entrada_busqueda.pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.X,
            expand=True,
        )

        self._entrada_busqueda.bind(
            "<KeyRelease>",
            self._on_buscar,
        )
        self._entrada_busqueda.bind(
            "<Return>",
            self._buscar_manual,
        )

        ttk.Button(
            frame_buscar,
            text="Buscar",
            command=self._buscar_manual,
        ).pack(side=tk.LEFT)

        ttk.Button(
            frame_buscar,
            text="Limpiar",
            command=self._limpiar_busqueda,
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Panel central: resultados.
        frame_resultados = ttk.LabelFrame(
            self,
            text="Personas encontradas",
            padding=10,
        )
        frame_resultados.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5,
        )

        self._lista_resultados = ttk.Treeview(
            frame_resultados,
            columns=("nombre", "usuario", "estado"),
            show="headings",
            height=7,
            selectmode="browse",
        )

        self._lista_resultados.heading("nombre", text="Nombre")
        self._lista_resultados.heading("usuario", text="Usuario")
        self._lista_resultados.heading("estado", text="Estado")

        self._lista_resultados.column(
            "nombre",
            width=220,
            anchor=tk.W,
        )
        self._lista_resultados.column(
            "usuario",
            width=160,
            anchor=tk.W,
        )
        self._lista_resultados.column(
            "estado",
            width=120,
            anchor=tk.CENTER,
        )

        self._lista_resultados.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        scroll_resultados = ttk.Scrollbar(
            frame_resultados,
            orient=tk.VERTICAL,
            command=self._lista_resultados.yview,
        )
        scroll_resultados.pack(side=tk.RIGHT, fill=tk.Y)

        self._lista_resultados.configure(
            yscrollcommand=scroll_resultados.set
        )

        ttk.Button(
            frame_resultados,
            text="Agregar amigo seleccionado",
            command=self._agregar_amigo_seleccionado,
        ).pack(side=tk.BOTTOM, pady=(8, 0))

        # Panel inferior: lista de amigos.
        frame_amigos = ttk.LabelFrame(
            self,
            text="Mis amigos",
            padding=10,
        )
        frame_amigos.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5,
        )

        self._lista_amigos = tk.Listbox(
            frame_amigos,
            height=5,
            font=("Arial", 10),
            activestyle="dotbox",
        )
        self._lista_amigos.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        scroll_amigos = ttk.Scrollbar(
            frame_amigos,
            orient=tk.VERTICAL,
            command=self._lista_amigos.yview,
        )
        scroll_amigos.pack(side=tk.RIGHT, fill=tk.Y)

        self._lista_amigos.configure(
            yscrollcommand=scroll_amigos.set
        )

        ttk.Button(
            frame_amigos,
            text="Actualizar amigos",
            command=self._refrescar_amigos,
        ).pack(side=tk.BOTTOM, pady=(8, 0))

        # Barra inferior de estado.
        self._etiqueta_estado = ttk.Label(
            self,
            text="Listo.",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5,
        )
        self._etiqueta_estado.pack(
            side=tk.BOTTOM,
            fill=tk.X,
        )

    # --------------------------------------------------
    # Búsqueda de usuarios
    # --------------------------------------------------

    def _on_buscar(self, event: tk.Event) -> None:
        """Actualiza los resultados mientras se escribe."""

        self._mostrar_resultados(
            self._entrada_busqueda.get()
        )

    def _buscar_manual(self, event=None) -> None:
        """Ejecuta la búsqueda mediante el botón o Enter."""

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

        try:
            resultados = self._servicio.buscar_usuarios(texto)

        except ErrorSocialUna as error:
            mostrar_error(str(error))
            self._etiqueta_estado.config(
                text="No fue posible realizar la búsqueda."
            )
            return

        for resultado in resultados:
            usuario: Usuario = resultado["usuario"]
            es_amigo: bool = resultado["es_amigo"]

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

        try:
            amigos = self._servicio.listar_mis_amigos()

        except ErrorSocialUna as error:
            mostrar_error(str(error))
            self._etiqueta_estado.config(
                text="No fue posible cargar la lista de amigos."
            )
            return

        for usuario in amigos:
            self._lista_amigos.insert(
                tk.END,
                f"{usuario.nombre} (@{usuario.nombre_usuario})",
            )

        self._etiqueta_estado.config(
            text=(
                f"Tu lista de amigos contiene "
                f"{len(amigos)} personas."
            )
        )
