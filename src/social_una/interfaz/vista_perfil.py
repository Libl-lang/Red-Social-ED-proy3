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
_BLANCO = "#FFFFFF"
_AZUL_CLARO = "#E8F1FD"


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
            "SocialProfile.Cancel.TButton",
            background="#E7EAF0",
            foreground=_MARINO,
            font=(_FUENTE, 10, "bold"),
            padding=(12, 8),
            borderwidth=0,
        )
        estilo.map(
            "SocialProfile.Cancel.TButton",
            background=[("active", "#D8DDE6"), ("pressed", "#C9D0DC")],
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
        dialogo.configure(bg=_BLANCO)
        dialogo.resizable(False, False)
        dialogo.transient(self.winfo_toplevel())

        contenedor = tk.Frame(
            dialogo,
            bg=_BLANCO,
            highlightthickness=1,
            highlightbackground="#91A7C2",
        )
        contenedor.pack(fill="both", expand=True)

        encabezado = tk.Frame(contenedor, bg=_MARINO, height=116)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)
        icono_candado = tk.Canvas(
            encabezado,
            width=86,
            height=82,
            bg=_MARINO,
            highlightthickness=0,
        )
        icono_candado.pack(side="left", padx=(18, 12), pady=(8, 18))
        icono_candado.create_oval(
            7, 3, 79, 75,
            outline=_BLANCO,
            width=3,
        )
        icono_candado.create_arc(
            31, 19, 55, 48,
            start=0,
            extent=180,
            style="arc",
            outline=_BLANCO,
            width=3,
        )
        icono_candado.create_rectangle(
            29, 34, 57, 57,
            fill=_BLANCO,
            outline=_BLANCO,
        )
        icono_candado.create_oval(
            40, 40, 46, 46,
            fill=_MARINO,
            outline=_MARINO,
        )
        icono_candado.create_rectangle(
            42, 44, 44, 51,
            fill=_MARINO,
            outline=_MARINO,
        )

        texto_encabezado = tk.Frame(encabezado, bg=_MARINO)
        texto_encabezado.pack(side="left", fill="y", pady=(22, 24))
        tk.Label(
            texto_encabezado,
            text="Cambiar contraseña",
            bg=_MARINO,
            fg=_BLANCO,
            font=(_FUENTE, 17, "bold"),
        ).pack(anchor="w")
        tk.Label(
            texto_encabezado,
            text="Protegé el acceso a tu cuenta",
            bg=_MARINO,
            fg="#E5EDF7",
            font=(_FUENTE, 10),
        ).pack(anchor="w", pady=(3, 0))

        decoracion = tk.Canvas(
            encabezado,
            height=28,
            bg=_MARINO,
            highlightthickness=0,
        )
        decoracion.place(relx=0, rely=1, relwidth=1, anchor="sw")
        decoracion.bind(
            "<Configure>",
            lambda evento: self._dibujar_ondas_dialogo(evento),
        )

        contenido = tk.Frame(contenedor, bg=_BLANCO, padx=30, pady=20)
        contenido.pack(fill="both", expand=True)
        etiquetas_campos = (
            "Contraseña actual",
            "Nueva contraseña",
            "Confirmar nueva contraseña",
        )
        campos = []
        for indice, texto in enumerate(etiquetas_campos):
            tk.Label(
                contenido,
                text=texto,
                bg=_BLANCO,
                fg=_MARINO,
                font=(_FUENTE, 10, "bold"),
            ).pack(anchor="w", pady=(0, 5))

            fila_campo = tk.Frame(
                contenido,
                bg=_BLANCO,
                highlightthickness=1,
                highlightbackground="#8EA2BE",
                highlightcolor=_AZUL,
            )
            fila_campo.pack(fill="x", pady=(0, 12 if indice != 1 else 8))
            campo = tk.Entry(
                fila_campo,
                show="*",
                font=(_FUENTE, 10),
                bg=_BLANCO,
                fg=_MARINO,
                insertbackground=_MARINO,
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
            )
            campo.pack(side="left", fill="x", expand=True, ipady=5, padx=(9, 0))
            campo.bind(
                "<FocusIn>",
                lambda evento: self._actualizar_borde_campo(
                    evento.widget.master,
                    enfocado=True,
                ),
            )
            campo.bind(
                "<FocusOut>",
                lambda evento: self._actualizar_borde_campo(
                    evento.widget.master,
                    enfocado=False,
                ),
            )
            ojo = tk.Canvas(
                fila_campo,
                width=30,
                height=26,
                bg=_BLANCO,
                highlightthickness=0,
                cursor="hand2",
            )
            ojo.pack(side="right", padx=(2, 5), pady=1)
            self._dibujar_ojo_contrasena(ojo, visible=False)
            ojo.bind(
                "<Button-1>",
                lambda evento, entrada=campo, icono=ojo: (
                    self._alternar_visibilidad_contrasena(entrada, icono)
                    if evento.widget.winfo_exists()
                    else None
                ),
            )
            campos.append(campo)

            if indice == 1:
                requisitos = tk.Frame(contenido, bg=_AZUL_CLARO)
                requisitos.pack(fill="x", pady=(0, 14))
                tk.Label(
                    requisitos,
                    text="ℹ",
                    bg=_AZUL_CLARO,
                    fg="#0874DD",
                    font=(_FUENTE, 16, "bold"),
                ).pack(side="left", padx=(10, 8), pady=8)
                texto_requisitos = tk.Frame(requisitos, bg=_AZUL_CLARO)
                texto_requisitos.pack(side="left", fill="x", pady=7)
                tk.Label(
                    texto_requisitos,
                    text="Requisitos de la nueva contraseña:",
                    bg=_AZUL_CLARO,
                    fg=_MARINO,
                    font=(_FUENTE, 9, "bold"),
                ).pack(anchor="w")
                tk.Label(
                    texto_requisitos,
                    text="Mínimo 6 caracteres.",
                    bg=_AZUL_CLARO,
                    fg=_MARINO,
                    font=(_FUENTE, 9),
                ).pack(anchor="w", pady=(2, 0))

        botones = tk.Frame(contenido, bg=_BLANCO)
        botones.pack(fill="x", pady=(8, 0))
        botones.columnconfigure(0, weight=3, uniform="dialog-buttons")
        botones.columnconfigure(1, weight=2, uniform="dialog-buttons")

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
            text="Guardar contraseña",
            style="SocialProfile.Save.TButton",
            command=guardar,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=2)
        ttk.Button(
            botones,
            text="Cancelar",
            style="SocialProfile.Cancel.TButton",
            command=cancelar,
        ).grid(row=0, column=1, sticky="ew", ipady=2)
        dialogo.protocol("WM_DELETE_WINDOW", cancelar)
        try:
            dialogo.geometry("500x555")
            dialogo.update_idletasks()
            padre = self.winfo_toplevel()
            x = padre.winfo_rootx() + (
                padre.winfo_width() - 500
            ) // 2
            y = padre.winfo_rooty() + (
                padre.winfo_height() - 555
            ) // 2
            dialogo.geometry(f"+{x}+{y}")
            dialogo.grab_set()
            campos[0].focus_set()
            self.wait_window(dialogo)
        finally:
            self._cambiando_contrasena = False

    @staticmethod
    def _dibujar_ondas_dialogo(evento: tk.Event) -> None:
        lienzo = evento.widget
        lienzo.delete("decoracion")
        ancho = max(evento.width, 1)
        alto = max(evento.height, 1)
        lienzo.create_line(
            0, alto * 0.88,
            ancho * 0.26, alto * 0.82,
            ancho * 0.55, alto * 0.28,
            ancho, alto * 0.12,
            smooth=True,
            splinesteps=24,
            fill=_BLANCO,
            width=5,
            tags="decoracion",
        )
        lienzo.create_line(
            0, alto,
            ancho * 0.26, alto * 0.94,
            ancho * 0.55, alto * 0.4,
            ancho, alto * 0.24,
            smooth=True,
            splinesteps=24,
            fill=_ROJO,
            width=7,
            tags="decoracion",
        )

    @staticmethod
    def _dibujar_ojo_contrasena(
        icono: tk.Canvas,
        *,
        visible: bool,
    ) -> None:
        icono.delete("ojo")
        icono.create_line(
            5, 13, 9, 8, 15, 6, 21, 8, 25, 13,
            21, 18, 15, 20, 9, 18, 5, 13,
            smooth=True,
            splinesteps=20,
            fill=_MARINO,
            width=2,
            tags="ojo",
        )
        icono.create_oval(
            12, 10, 18, 16,
            outline=_MARINO,
            width=2,
            tags="ojo",
        )
        if not visible:
            icono.create_line(
                7, 21, 23, 5,
                fill=_MARINO,
                width=2,
                tags=("ojo", "oculto"),
            )

    @staticmethod
    def _actualizar_borde_campo(
        marco: tk.Frame,
        *,
        enfocado: bool,
    ) -> None:
        marco.configure(
            highlightbackground=_AZUL if enfocado else "#8EA2BE",
            highlightcolor=_AZUL,
        )

    def _alternar_visibilidad_contrasena(
        self,
        campo: tk.Entry,
        icono: tk.Canvas,
    ) -> None:
        visible = not getattr(icono, "_contrasena_visible", False)
        campo.configure(show="" if visible else "*")
        icono._contrasena_visible = visible
        self._dibujar_ojo_contrasena(icono, visible=visible)

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
