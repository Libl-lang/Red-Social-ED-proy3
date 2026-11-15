"""Carga iconos PNG incluidos con la interfaz de Social UNA."""

from pathlib import Path
import tkinter as tk


_DIRECTORIO_ICONOS = Path(__file__).parent / "recursos" / "iconos"


def cargar_icono(
    padre: tk.Misc,
    nombre: str,
    divisor: int = 1,
) -> tk.PhotoImage:
    """Carga un icono y lo reduce uniformemente si el control lo requiere."""
    imagen = tk.PhotoImage(
        master=padre,
        file=str(_DIRECTORIO_ICONOS / f"{nombre}.png"),
    )
    if divisor > 1:
        imagen = imagen.subsample(divisor, divisor)
    return imagen
