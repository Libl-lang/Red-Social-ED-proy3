"""Funciones reunidas para mensajes gráficos de la aplicación.

Todas las pantallas deben usar estas funciones para verse igual.
Solo la capa de interfaz las usa; los servicios nunca."""

from tkinter import messagebox


def mostrar_error(mensaje: str) -> None:
    """Muestra una ventana de error con el mensaje recibido."""
    messagebox.showerror("Error", mensaje)


def mostrar_informacion(mensaje: str) -> None:
    """Muestra una ventana informativa con el mensaje recibido."""
    messagebox.showinfo("Información", mensaje)


def confirmar(pregunta: str) -> bool:
    """Muestra una pregunta con botones Sí y No; devuelve True si la
    persona elige Sí y False si elige No."""
    return messagebox.askyesno("Confirmar", pregunta)
