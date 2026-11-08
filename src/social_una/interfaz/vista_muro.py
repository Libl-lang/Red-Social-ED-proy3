
"""Define la pantalla del muro de publicaciones y no contiene lógica de negocio,
   solo llama al servicio."""

import tkinter as tk
from datetime import datetime
from tkinter import ttk
from social_una.dominio.errores import ErrorSocialUna
from social_una.interfaz import alertas
from social_una.servicios.servicio_publicaciones import LARGO_MAXIMO_PUBLICACION, ServicioPublicaciones


class VistaMuro(ttk.Frame):

    """Muestra el muro de publicaciones y permite alternar entre muro general y muro personal, y publicar un mensaje."""

    def __init__(self, padre: tk.Misc, servicio: ServicioPublicaciones) -> None:
        super().__init__(padre)
        self._servicio = servicio
        self._modo = tk.StringVar(value="general")
        self._crear_widgets()

    def _crear_widgets(self) -> None:
        # barra superior con modo general/personal
        barra = ttk.Frame(self)
        barra.pack(padx=8, pady=4)
        ttk.Radiobutton(barra, text="Muro general", variable=self._modo, value="general", command=self.refrescar).pack(side="left", padx=2)
        ttk.Radiobutton(barra, text="Mi muro", variable=self._modo, value="personal", command=self.refrescar).pack(side="left", padx=2)

        # zona del muro con área de texto y scroll
        muro = ttk.Frame(self)
        
        muro.pack(fill="both", expand=True, padx=8, pady=4)
        self._area_muro = tk.Text(muro, height=15, width=60, wrap="word", state="disabled")
        self._area_muro.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(muro, orient="vertical", command=self._area_muro.yview)
        scroll.pack(side="right", fill="y")
        self._area_muro.configure(yscrollcommand=scroll.set)

        # etiqueta y caja de texto para publicar
        ttk.Label(self, text="Escribe una publicación:").pack(padx=8, pady=4)
        self._caja_texto = tk.Text(self, height=4, width=60, wrap="word")
        self._caja_texto.pack(fill="x", padx=8)
        self._caja_texto.bind("<KeyRelease>", self._actualizar_contador)

        # barra inferior con contador y botón publicar
        barra_inferior = ttk.Frame(self)
        barra_inferior.pack(padx=8, pady=4)
        self._contador = ttk.Label(barra_inferior, text=f"0/{LARGO_MAXIMO_PUBLICACION}")
        self._contador.pack(side="left")
        ttk.Button(barra_inferior, text="Publicar", command=self._al_publicar).pack(side="right")

    def refrescar(self) -> None:
        """Vuelve a leer el servicio y redibuja el muro; lo llama quien muestre la pantalla."""
        try:
            if self._modo.get() == "personal":
                publicaciones = self._servicio.obtener_muro_personal()
            else:
                publicaciones = self._servicio.obtener_muro()
        except ErrorSocialUna as error:
            alertas.mostrar_error(str(error))
            self._mostrar_texto("")
            return
        if not publicaciones:
            self._mostrar_texto("Todavía no hay publicaciones.")
            return
        bloques = []
        for publicacion in publicaciones:
            nombre = self._servicio.obtener_nombre_autor(publicacion.id_autor)
            bloque = f"{nombre} - {self._formatear_fecha(publicacion.fecha_creacion)}\n{publicacion.texto}"
            bloques.append(bloque)
        self._mostrar_texto("\n\n".join(bloques))

    def _al_publicar(self) -> None:
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
        cantidad = len(self._caja_texto.get("1.0", "end-1c"))
        self._contador.configure(text=f"{cantidad}/{LARGO_MAXIMO_PUBLICACION}")

    def _mostrar_texto(self, contenido: str) -> None:
        self._area_muro.configure(state="normal")
        self._area_muro.delete("1.0", "end")
        self._area_muro.insert("1.0", contenido)
        self._area_muro.configure(state="disabled")

    @staticmethod
    def _formatear_fecha(fecha_iso: str) -> str:
        try:
            return datetime.fromisoformat(fecha_iso).astimezone().strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return fecha_iso
