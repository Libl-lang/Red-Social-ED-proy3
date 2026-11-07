import tkinter as tk
from tkinter import ttk, messagebox

class VentanaPrincipal(tk.Toplevel):
    """Ventana principal de Social UNA despues de iniciar sesion."""

    def __init__(
        self,
        ventana_padre,
        usuario,
        servicio_autenticacion,
        al_cerrar_sesion
    ):
        super().__init__(ventana_padre)

        self._usuario = usuario
        self._servicio = servicio_autenticacion
        self._al_cerrar_sesion = al_cerrar_sesion
        self._cerrando = False

        self.title("Social UNA - Inicio")
        self.geometry("850x550")
        self.minsize(700, 450)
        self.configure(bg="#eef2f7")

        self._centrar_ventana()
        self._crear_interfaz()

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cerrar_sesion
        )

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla."""

        self.update_idletasks()

        ancho = 850
        alto = 550

        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2

        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _crear_interfaz(self):
        """Construye los componentes de la ventana principal."""

        encabezado = tk.Frame(
            self,
            bg="#17365d",
            height=85
        )
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        tk.Label(
            encabezado,
            text="SOCIAL UNA",
            bg="#17365d",
            fg="white",
            font=("Arial", 22, "bold")
        ).pack(side="left", padx=25, pady=20)

        tk.Label(
            encabezado,
            text=f"Hola, {self._usuario.nombre}",
            bg="#17365d",
            fg="white",
            font=("Arial", 11)
        ).pack(side="right", padx=25)

        contenido = tk.Frame(
            self,
            bg="#eef2f7",
            padx=35,
            pady=30
        )
        contenido.pack(fill="both", expand=True)

        tk.Label(
            contenido,
            text="Bienvenido a Social UNA",
            bg="#eef2f7",
            fg="#17365d",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(5, 8))

        tk.Label(
            contenido,
            text="Tu espacio de conexion con la comunidad universitaria.",
            bg="#eef2f7",
            fg="#64748b",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 25))

        tarjeta = tk.Frame(
            contenido,
            bg="white",
            padx=25,
            pady=25
        )
        tarjeta.pack(fill="x", pady=10)

        tk.Label(
            tarjeta,
            text="Mi perfil",
            bg="white",
            fg="#17365d",
            font=("Arial", 15, "bold")
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            tarjeta,
            text=f"Nombre: {self._usuario.nombre}",
            bg="white",
            fg="#334155",
            font=("Arial", 11)
        ).pack(anchor="w", pady=4)

        tk.Label(
            tarjeta,
            text=f"Usuario: {self._usuario.nombre_usuario}",
            bg="white",
            fg="#334155",
            font=("Arial", 11)
        ).pack(anchor="w", pady=4)

        opciones = tk.Frame(
            contenido,
            bg="#eef2f7"
        )
        opciones.pack(fill="x", pady=20)

        estilo = ttk.Style(self)
        estilo.configure(
            "Opcion.TButton",
            font=("Arial", 11, "bold"),
            padding=15
        )

        ttk.Button(
            opciones,
            text="Publicaciones",
            style="Opcion.TButton",
            state="disabled"
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ttk.Button(
            opciones,
            text="Amistades",
            style="Opcion.TButton",
            state="disabled"
        ).pack(side="left", expand=True, fill="x", padx=8)

        ttk.Button(
            opciones,
            text="Cerrar sesion",
            style="Opcion.TButton",
            command=self._cerrar_sesion
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

        tk.Label(
            contenido,
            text="Las secciones de publicaciones y amistades se habilitaran "
                 "cuando se integren los modulos correspondientes.",
            bg="#eef2f7",
            fg="#64748b",
            font=("Arial", 9),
            wraplength=750
        ).pack(anchor="w", pady=10)

    def _cerrar_sesion(self):
        """Cierra la sesion y regresa a la ventana de acceso."""

        if self._cerrando:
            return

        confirmar = messagebox.askyesno(
            "Cerrar sesion",
            "¿Desea cerrar su sesion?"
        )

        if not confirmar:
            return

        self._cerrando = True

        try:
            self._servicio.cerrar_sesion()
            self.destroy()
            self._al_cerrar_sesion()

        except Exception as error:
            self._cerrando = False
            messagebox.showerror(
                "Error",
                f"No se pudo cerrar la sesion: {error}"
            )
