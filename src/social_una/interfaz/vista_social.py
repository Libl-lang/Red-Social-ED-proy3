"""
Vista social de Social UNA (Modulo 2).

Interfaz grafica en Tkinter para buscar usuarios, agregar amigos y ver
la lista de amigos del usuario activo. Captura errores de negocio y los
muestra usando alertas.py.
"""

import tkinter as tk
from tkinter import ttk

from social_una.dominio.errores import ErrorSocialUna
from social_una.dominio.modelos import Usuario
from social_una.interfaz.alertas import mostrar_error, mostrar_informacion
from social_una.servicios.servicio_social import ServicioSocial


class VistaSocial:
    """
    Ventana de interaccion social: buscador de usuarios, agregar amigos,
    y lista de amigos del usuario activo.
    """

    def __init__(
        self,
        root: tk.Tk | tk.Toplevel,
        servicio: ServicioSocial,
    ) -> None:
        """
        Inicializa la vista social.

        Args:
            root: Ventana principal o Toplevel de Tkinter.
            servicio: ServicioSocial para operaciones de negocio.
        """
        self._root = root
        # Panel medio: resultados de busqueda
        frame_resultados = ttk.LabelFrame(
            self._root, text="Resultados de busqueda", padding="10"
        )
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._lista_resultados = ttk.Treeview(
            frame_resultados,
            columns=("nombre", "usuario", "amigo"),
            show="headings",
            height=8,
        )
        self._lista_resultados.heading("nombre", text="Nombre")
        self._lista_resultados.heading("usuario", text="Usuario")
        self._lista_resultados.heading("amigo", text="Estado")
        self._lista_resultados.column("nombre", width=200)
        self._lista_resultados.column("usuario", width=150)
        self._lista_resultados.column("amigo", width=100)
        self._lista_resultados.pack(fill=tk.BOTH, expand=True)

        scroll_resultados = ttk.Scrollbar(
            frame_resultados, orient=tk.VERTICAL, command=self._lista_resultados.yview
        )
        self._lista_resultados.configure(yscrollcommand=scroll_resultados.set)
        scroll_resultados.pack(side=tk.RIGHT, fill=tk.Y)

        btn_agregar = ttk.Button(
            frame_resultados, text="Agregar amigo", command=self._agregar_amigo_seleccionado
        )
        btn_agregar.pack(pady=(5, 0))

        # Panel inferior: amigos del usuario activo
        frame_amigos = ttk.LabelFrame(
            self._root, text="Mis amigos", padding="10"
        )
        frame_amigos.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _mostrar_resultados(self, texto: str) -> None:
        """Muestra los resultados de busqueda en la lista."""
        # Limpiar lista
        for item in self._lista_resultados.get_children():
            self._lista_resultados.delete(item)

        try:
            resultados = self._servicio.buscar_usuarios(texto)
        except ErrorSocialUna as e:
            mostrar_error(str(e))
            return

        for item in resultados:
            u: Usuario = item["usuario"]
            es_amigo: bool = item["es_amigo"]
            estado = "Ya es amigo" if es_amigo else "No es amigo"
            self._lista_resultados.insert(
                "", tk.END, values=(u.nombre, u.nombre_usuario, estado),
                tags=(str(u.id_usuario),),
            )

    def _agregar_amigo_seleccionado(self) -> None:
        """Agrega como amigo al usuario seleccionado en la lista de resultados."""
        seleccion = self._lista_resultados.selection()
        if not seleccion:
            mostrar_error("Selecciona un usuario de la lista para agregarlo como amigo.")
            return

        item_id = seleccion[0]
        tags = self._lista_resultados.item(item_id, "tags")
        if not tags:
            return
        id_amigo = int(tags[0])

        try:
            self._servicio.agregar_amigo(id_amigo)
        except ErrorSocialUna as e:
            mostrar_error(str(e))
            return

        mostrar_informacion("Amigo agregado correctamente.")
        self._refrescar_amigos()
        self._entrada_busqueda.delete(0, tk.END)
        self._mostrar_resultados("")

    def _refrescar_amigos(self) -> None:
        """Refresca la lista de amigos del usuario activo."""
        self._lista_amigos.delete(0, tk.END)

        try:
            amigos = self._servicio.listar_mis_amigos()
        except ErrorSocialUna as e:
            mostrar_error(str(e))
            return

        for u in amigos:
            self._lista_amigos.insert(tk.END, f"{u.nombre} ({u.nombre_usuario})")

        self._etiqueta_estado.config(
            text=f"Usuario activo: {self._servicio._usuario_actual().nombre} | "
            f"Amigos: {len(amigos)}"
        )
        self._lista_amigos = tk.Listbox(frame_amigos, height=6)
        self._lista_amigos.pack(fill=tk.BOTH, expand=True)

        # Barra de estado
        self._etiqueta_estado = ttk.Label(self._root, text="", relief=tk.SUNKEN)
        self._etiqueta_estado.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Acciones ---

    def _on_buscar(self, event: tk.Event) -> None:
        """Se ejecuta al escribir en el cuadro de busqueda."""
        texto = self._entrada_busqueda.get()
        self._mostrar_resultados(texto)
        self._servicio = servicio

        self._root.title("Social UNA - Amistades")
        self._root.geometry("600x500")

        self._crear_interfaz()
        self._refrescar_amigos()

    # --- Construccion de la interfaz ---

    def _crear_interfaz(self) -> None:
        """Crea todos los widgets de la ventana."""
        # Panel superior: buscador
        frame_buscar = ttk.Frame(self._root, padding="10")
        frame_buscar.pack(fill=tk.X)

        ttk.Label(frame_buscar, text="Buscar usuarios:").pack(side=tk.LEFT)

        self._entrada_busqueda = ttk.Entry(frame_buscar, width=40)
        self._entrada_busqueda.pack(side=tk.LEFT, padx=(5, 10))
        self._entrada_busqueda.bind("<KeyRelease>", self._on_buscar)

        ttk.Button(
            frame_buscar, text="Refrescar amigos", command=self._refrescar_amigos
        ).pack(side=tk.RIGHT)
