"""Vista de perfil y acciones de cuenta de Social UNA."""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from social_una.dominio.errores import (
    ErrorRecuperacionTransaccion,
    ErrorSocialUna,
)
from social_una.dominio.modelos import Usuario
from social_una.interfaz.iconos import cargar_icono
from social_una.servicios.servicio_autenticacion import ServicioAutenticacion
from social_una.servicios.servicio_cuenta import ServicioCuenta


_MARINO = "#102A4C"
_AZUL = "#225EA8"
_ROJO = "#C8102E"
_FONDO = "#F3F6FA"
_BORDE = "#CFE0F1"
_SUAVE = "#536B87"
_FUENTE = "Segoe UI"


class VistaPerfil(ttk.Frame):
    """Muestra los datos del usuario y permite eliminar su cuenta."""

    def __init__(
        self,
        padre: tk.Misc,
        usuario: Usuario,
        autenticacion: ServicioAutenticacion,
        servicio_cuenta: ServicioCuenta,
        al_cerrar_sesion,
        al_eliminar_cuenta,
        al_fallo_recuperacion,
    ) -> None:
        super().__init__(padre)
        self._usuario = usuario
        self._autenticacion = autenticacion
        self._servicio_cuenta = servicio_cuenta
        self._al_cerrar_sesion = al_cerrar_sesion
        self._al_eliminar_cuenta = al_eliminar_cuenta
        self._al_fallo_recuperacion = al_fallo_recuperacion
        self._eliminando = False
        self._cambiando_contrasena = False
        self._icono_eliminar = cargar_icono(self, "eliminar", 3)

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure(
            "SocialProfile.Logout.TButton",
            background=_AZUL,
            foreground="white",
            font=(_FUENTE, 10, "bold"),
            padding=(12, 8),
            borderwidth=0,
        )
        estilo.configure(
            "SocialProfile.Save.TButton",
            background=_AZUL,
            foreground="white",
            font=(_FUENTE, 10, "bold"),
            padding=(12, 8),
            borderwidth=0,
        )
        estilo.map(
            "SocialProfile.Save.TButton",
            background=[("active", "#1D416B"), ("pressed", _MARINO)],
        )
        estilo.configure(
            "SocialProfile.Delete.TButton",
            background=_ROJO,
            foreground="white",
            font=(_FUENTE, 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        estilo.map(
            "SocialProfile.Delete.TButton",
            background=[("active", "#A90E27"), ("pressed", "#8F0B20")],
        )

        contenido = tk.Frame(self, bg=_FONDO)
        contenido.pack(fill="both", expand=True, padx=4, pady=4)

        encabezado = tk.Frame(contenido, bg=_FONDO)
        encabezado.pack(fill="x", pady=(4, 14))
        avatar = tk.Canvas(
            encabezado,
            width=44,
            height=44,
            bg=_FONDO,
            highlightthickness=0,
        )
        avatar.create_oval(2, 2, 42, 42, fill=_MARINO, outline="")
        iniciales = "".join(
            parte[0] for parte in self._usuario.nombre.split()[:2]
        ).upper()
        avatar.create_text(
            22,
            22,
            text=iniciales or "?",
            fill="white",
            font=(_FUENTE, 12, "bold"),
        )
        avatar.pack(side="left", padx=(4, 10))
        titulo = tk.Frame(encabezado, bg=_FONDO)
        titulo.pack(side="left", fill="y")
        tk.Label(
            titulo,
            text="Mi perfil",
            bg=_FONDO,
            fg=_MARINO,
            font=(_FUENTE, 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            titulo,
            text="Información y configuración de tu cuenta",
            bg=_FONDO,
            fg=_SUAVE,
            font=(_FUENTE, 10),
        ).pack(anchor="w")

        tarjeta = tk.Frame(
            contenido,
            bg="white",
            highlightthickness=1,
            highlightbackground=_BORDE,
        )
        tarjeta.pack(fill="x")
        identidad = tk.Frame(tarjeta, bg="white")
        identidad.pack(fill="x", padx=20, pady=18)
        tk.Label(
            identidad,
            text=self._usuario.nombre,
            bg="white",
            fg=_MARINO,
            font=(_FUENTE, 16, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            identidad,
            text=f"@{self._usuario.nombre_usuario}",
            bg="white",
            fg=_SUAVE,
            font=(_FUENTE, 10),
            anchor="w",
        ).pack(anchor="w", pady=(3, 10))
        tk.Label(
            identidad,
            text=f"Miembro desde: {self._fecha_registro()}",
            bg="white",
            fg=_SUAVE,
            font=(_FUENTE, 9),
            anchor="w",
        ).pack(anchor="w")

        tk.Frame(tarjeta, bg=_BORDE, height=1).pack(fill="x", padx=18)
        fila_cambio = tk.Frame(
            tarjeta,
            bg="white",
            cursor="hand2",
            takefocus=True,
        )
        fila_cambio.pack(fill="x", padx=20, pady=(14, 0))
        icono_candado = tk.Canvas(
            fila_cambio,
            width=24,
            height=26,
            bg="white",
            highlightthickness=0,
        )
        icono_candado.create_arc(
            5, 1, 19, 17,
            start=0,
            extent=180,
            style="arc",
            outline=_AZUL,
            width=2,
        )
        icono_candado.create_rectangle(
            5, 10, 19, 23,
            outline=_AZUL,
            width=2,
        )
        icono_candado.create_oval(
            11, 14, 13, 16,
            fill=_AZUL,
            outline=_AZUL,
        )
        icono_candado.pack(side="left", padx=(0, 12))
        texto_cambio = tk.Frame(fila_cambio, bg="white")
        texto_cambio.pack(side="left", fill="x", expand=True)
        tk.Label(
            texto_cambio,
            text="Cambiar contraseña",
            bg="white",
            fg=_MARINO,
            font=(_FUENTE, 11, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            texto_cambio,
            text="Actualiza la contraseña de tu cuenta.",
            bg="white",
            fg=_SUAVE,
            font=(_FUENTE, 9),
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))
        flecha_cambio = tk.Label(
            fila_cambio,
            text="›",
            bg="white",
            fg=_SUAVE,
            font=(_FUENTE, 20),
        )
        flecha_cambio.pack(side="right", padx=(12, 0))
        widgets_fila_cambio = (
            fila_cambio,
            icono_candado,
            texto_cambio,
            *texto_cambio.winfo_children(),
            flecha_cambio,
        )
        for widget in widgets_fila_cambio:
            widget.bind("<Button-1>", self._activar_cambio_contrasena)
        fila_cambio.bind("<Return>", self._activar_cambio_contrasena)
        fila_cambio.bind("<space>", self._activar_cambio_contrasena)

        tk.Frame(tarjeta, bg=_BORDE, height=1).pack(
            fill="x",
            padx=18,
            pady=(14, 0),
        )
        fila_sesion = tk.Frame(tarjeta, bg="white")
        fila_sesion.pack(fill="x", padx=20, pady=14)
        texto_sesion = tk.Frame(fila_sesion, bg="white")
        texto_sesion.pack(side="left", fill="x", expand=True)
        tk.Label(
            texto_sesion,
            text="Cerrar sesión",
            bg="white",
            fg=_MARINO,
            font=(_FUENTE, 11, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            texto_sesion,
            text="Vuelve a la pantalla de acceso",
            bg="white",
            fg=_SUAVE,
            font=(_FUENTE, 9),
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))
        ttk.Button(
            fila_sesion,
            text="Cerrar sesión",
            style="SocialProfile.Logout.TButton",
            command=self._al_cerrar_sesion,
        ).pack(side="right", padx=(12, 0))

        peligro = tk.Frame(
            contenido,
            bg="#FFF8F8",
            highlightthickness=1,
            highlightbackground="#E6A7B1",
        )
        peligro.pack(fill="x", pady=(16, 0))
        tk.Label(
            peligro,
            text="Zona de peligro",
            bg="#FFF8F8",
            fg=_ROJO,
            font=(_FUENTE, 13, "bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(13, 5))
        self._aviso_eliminacion = tk.Label(
            peligro,
            text=(
                "Eliminar tu cuenta es una acción permanente. Se eliminarán "
                "tu usuario, tus publicaciones y todas tus relaciones de amistad."
            ),
            bg="#FFF8F8",
            fg=_MARINO,
            font=(_FUENTE, 9),
            justify="left",
            wraplength=640,
            anchor="w",
        )
        self._aviso_eliminacion.pack(fill="x", padx=16)
        self._boton_eliminar = ttk.Button(
            peligro,
            text="Eliminar mi cuenta",
            image=self._icono_eliminar,
            compound="left",
            style="SocialProfile.Delete.TButton",
            command=self._solicitar_eliminacion,
        )
        self._boton_eliminar.pack(anchor="w", padx=16, pady=(12, 14))
        self.bind("<Configure>", self._ajustar_texto_advertencia)

    def _ajustar_texto_advertencia(self, evento: tk.Event) -> None:
        if evento.widget is self:
            self._aviso_eliminacion.configure(
                wraplength=max(evento.width - 48, 220)
            )

    def _fecha_registro(self) -> str:
        try:
            return datetime.fromisoformat(
                self._usuario.fecha_registro
            ).strftime("%d/%m/%Y")
        except ValueError:
            return self._usuario.fecha_registro

    def _activar_cambio_contrasena(self, evento: tk.Event) -> None:
        if evento.widget.winfo_exists():
            self._abrir_dialogo_cambio_contrasena()

    def _abrir_dialogo_cambio_contrasena(self) -> None:
        if self._cambiando_contrasena:
            return
        self._cambiando_contrasena = True
        dialogo = tk.Toplevel(self)
        dialogo.title("Cambiar contraseña")
        dialogo.configure(bg=_FONDO)
        dialogo.resizable(False, False)
        dialogo.transient(self.winfo_toplevel())

        contenido = tk.Frame(dialogo, bg=_FONDO, padx=22, pady=18)
        contenido.pack(fill="both", expand=True)
        tk.Label(
            contenido,
            text="Actualiza la contraseña de tu cuenta",
            bg=_FONDO,
            fg=_MARINO,
            font=(_FUENTE, 12, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        campos = []
        for texto in (
            "Contraseña actual",
            "Nueva contraseña",
            "Confirmar nueva contraseña",
        ):
            tk.Label(
                contenido,
                text=texto,
                bg=_FONDO,
                fg=_MARINO,
                font=(_FUENTE, 9, "bold"),
            ).pack(anchor="w", pady=(0, 4))
            campo = ttk.Entry(contenido, show="*", width=36)
            campo.pack(fill="x", pady=(0, 10))
            campos.append(campo)

        botones = tk.Frame(contenido, bg=_FONDO)
        botones.pack(fill="x", pady=(4, 0))

        def cancelar() -> None:
            self._cancelar_dialogo_cambio_contrasena(dialogo)

        def guardar() -> None:
            try:
                self._autenticacion.cambiar_contrasena(
                    campos[0].get(),
                    campos[1].get(),
                    campos[2].get(),
                )
            except ErrorSocialUna as error:
                messagebox.showerror(
                    "No se pudo cambiar la contraseña",
                    str(error),
                    parent=dialogo,
                )
                return

            dialogo.destroy()
            messagebox.showinfo(
                "Contraseña actualizada",
                "Tu contraseña se cambió correctamente.",
                parent=self.winfo_toplevel(),
            )

        ttk.Button(
            botones,
            text="Cancelar",
            command=cancelar,
        ).pack(side="right", padx=(8, 0))
        ttk.Button(
            botones,
            text="Guardar cambios",
            style="SocialProfile.Save.TButton",
            command=guardar,
        ).pack(side="right")
        dialogo.protocol("WM_DELETE_WINDOW", cancelar)
        try:
            dialogo.update_idletasks()
            padre = self.winfo_toplevel()
            x = padre.winfo_rootx() + (
                padre.winfo_width() - dialogo.winfo_reqwidth()
            ) // 2
            y = padre.winfo_rooty() + (
                padre.winfo_height() - dialogo.winfo_reqheight()
            ) // 2
            dialogo.geometry(f"+{x}+{y}")
            dialogo.grab_set()
            campos[0].focus_set()
            self.wait_window(dialogo)
        finally:
            self._cambiando_contrasena = False

    @staticmethod
    def _cancelar_dialogo_cambio_contrasena(dialogo: tk.Toplevel) -> None:
        dialogo.destroy()

    def _solicitar_eliminacion(self) -> None:
        if self._eliminando:
            return
        self._eliminando = True
        self._boton_eliminar.configure(state="disabled")
        contrasena = ""
        try:
            parent = self.winfo_toplevel()
            advertencia = (
                "Esta acción eliminará permanentemente tu cuenta, todas tus "
                "publicaciones y todas tus amistades. ¿Deseas continuar?"
            )
            if not messagebox.askyesno(
                "Eliminar mi cuenta",
                advertencia,
                parent=parent,
            ):
                return

            contrasena = simpledialog.askstring(
                "Confirmar identidad",
                "Ingresa tu contraseña actual:",
                show="*",
                parent=parent,
            )
            if contrasena is None:
                return

            self._autenticacion.verificar_contrasena_actual(contrasena)
            if not messagebox.askyesno(
                "Confirmación final",
                "La eliminación es permanente y no se puede deshacer. "
                "¿Confirmas que deseas eliminar tu cuenta?",
                parent=parent,
            ):
                return

            self._servicio_cuenta.eliminar_mi_cuenta(contrasena)
            self._al_eliminar_cuenta()
        except ErrorRecuperacionTransaccion as error:
            self._al_fallo_recuperacion(str(error))
        except ErrorSocialUna as error:
            messagebox.showerror(
                "No se pudo eliminar la cuenta",
                str(error),
                parent=self.winfo_toplevel(),
            )
        finally:
            contrasena = ""
            if self.winfo_exists():
                self._eliminando = False
                self._boton_eliminar.configure(state="normal")
