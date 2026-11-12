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
        self.geometry("430x520")
        self.resizable(False, False)
        self.configure(bg="#eef2f7")

        self._centrar_ventana()
        self._configurar_estilos()
        self.mostrar_login()

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla."""

        self.update_idletasks()

        ancho = 430
        alto = 520

        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2

        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _configurar_estilos(self):
        """Configura los estilos visuales."""

        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(
            "Titulo.TLabel",
            background="white",
            foreground="#17365d",
            font=("Arial", 23, "bold")
        )

        estilo.configure(
            "Subtitulo.TLabel",
            background="white",
            foreground="#64748b",
            font=("Arial", 10)
        )

        estilo.configure(
            "Campo.TLabel",
            background="white",
            foreground="#334155",
            font=("Arial", 10, "bold")
        )

        estilo.configure(
            "Principal.TButton",
            font=("Arial", 10, "bold"),
            padding=10
        )

    def _limpiar_ventana(self):
        """Elimina los componentes de la vista actual."""

        for componente in self.winfo_children():
            componente.destroy()

    def _crear_encabezado(self, subtitulo):
        """Construye el encabezado de la ventana."""

        ttk.Label(
            self.panel,
            text="SOCIAL UNA",
            style="Titulo.TLabel"
        ).pack(pady=(30, 8))

        ttk.Label(
            self.panel,
            text=subtitulo,
            style="Subtitulo.TLabel"
        ).pack(pady=(0, 25))

    def volver_al_login(self):
        """Vuelve a mostrar la ventana de acceso."""

        self.deiconify()
        self.mostrar_login()

    def _alternar_contrasena(self, campo, boton, atributo_estado):
        """Muestra u oculta la contraseña del campo indicado."""

        visible = not getattr(self, atributo_estado, False)
        setattr(self, atributo_estado, visible)

        campo.configure(show="" if visible else "*")
        boton.configure(text="🙈" if visible else "👁")

    def mostrar_login(self):
        """Muestra el formulario de inicio de sesion."""

        self._limpiar_ventana()

        self.panel = tk.Frame(
            self,
            bg="white",
            padx=35,
            pady=20
        )
        self.panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        self._crear_encabezado("Inicia sesion en tu cuenta")

        ttk.Label(
            self.panel,
            text="Nombre de usuario",
            style="Campo.TLabel"
        ).pack(anchor="w", pady=(5, 6))

        self.txt_usuario = ttk.Entry(
            self.panel,
            font=("Arial", 11)
        )
        self.txt_usuario.pack(fill="x", ipady=7)

        ttk.Label(
            self.panel,
            text="Contrasena",
            style="Campo.TLabel"
        ).pack(anchor="w", pady=(18, 6))

        fila_contrasena = tk.Frame(self.panel, bg="white")
        fila_contrasena.pack(fill="x")

        self.txt_contrasena = ttk.Entry(
            fila_contrasena,
            font=("Arial", 11),
            show="*"
        )
        self.txt_contrasena.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        self._contrasena_visible_login = False

        self.btn_mostrar_login = ttk.Button(
            fila_contrasena,
            text="👁",
            width=4,
            command=lambda: self._alternar_contrasena(
                self.txt_contrasena,
                self.btn_mostrar_login,
                "_contrasena_visible_login"
            )
        )
        self.btn_mostrar_login.pack(side="right", padx=(5, 0))

        ttk.Button(
            self.panel,
            text="Iniciar sesion",
            style="Principal.TButton",
            command=self._iniciar_sesion
        ).pack(fill="x", pady=(20, 10))

        ttk.Button(
            self.panel,
            text="Crear una cuenta nueva",
            command=self.mostrar_registro
        ).pack(fill="x")

        self.txt_usuario.focus_set()
        self.txt_usuario.delete(0, tk.END)
        self.txt_contrasena.delete(0, tk.END)

        self.bind(
            "<Return>",
            lambda evento: self._iniciar_sesion()
        )

    def mostrar_registro(self):
        """Muestra el formulario para registrar usuarios."""

        self._limpiar_ventana()
        self.unbind("<Return>")

        self.panel = tk.Frame(
            self,
            bg="white",
            padx=35,
            pady=15
        )
        self.panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        self._crear_encabezado("Crea tu cuenta")

        ttk.Label(
            self.panel,
            text="Nombre completo",
            style="Campo.TLabel"
        ).pack(anchor="w", pady=(3, 5))

        self.txt_nombre = ttk.Entry(
            self.panel,
            font=("Arial", 11)
        )
        self.txt_nombre.pack(fill="x", ipady=6)

        ttk.Label(
            self.panel,
            text="Nombre de usuario",
            style="Campo.TLabel"
        ).pack(anchor="w", pady=(12, 5))

        self.txt_usuario_registro = ttk.Entry(
            self.panel,
            font=("Arial", 11)
        )
        self.txt_usuario_registro.pack(fill="x", ipady=6)

        ttk.Label(
            self.panel,
            text="Contrasena (minimo 6 caracteres)",
            style="Campo.TLabel"
        ).pack(anchor="w", pady=(12, 5))

        fila_contrasena = tk.Frame(self.panel, bg="white")
        fila_contrasena.pack(fill="x")

        self.txt_contrasena_registro = ttk.Entry(
            fila_contrasena,
            font=("Arial", 11),
            show="*"
        )
        self.txt_contrasena_registro.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6
        )

        self._contrasena_visible_registro = False

        self.btn_mostrar_registro = ttk.Button(
            fila_contrasena,
            text="👁",
            width=4,
            command=lambda: self._alternar_contrasena(
                self.txt_contrasena_registro,
                self.btn_mostrar_registro,
                "_contrasena_visible_registro"
            )
        )
        self.btn_mostrar_registro.pack(side="right", padx=(5, 0))

        ttk.Button(
            self.panel,
            text="Registrarme",
            style="Principal.TButton",
            command=self._registrar_usuario
        ).pack(fill="x", pady=(20, 10))

        ttk.Button(
            self.panel,
            text="Volver al inicio de sesion",
            command=self.mostrar_login
        ).pack(fill="x")

        self.txt_nombre.focus_set()

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

