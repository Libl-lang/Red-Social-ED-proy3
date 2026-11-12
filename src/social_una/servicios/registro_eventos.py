"""
Registro de eventos de Social UNA.

Centraliza los registros de operaciones importantes del sistema.
No almacena contraseñas, hashes ni contenido privado.
"""

import logging
from pathlib import Path


def crear_registrador(ruta_datos: str | Path) -> logging.Logger:
    """
    Configura y devuelve el registrador de eventos de Social UNA.

    Los registros se guardan en datos/social_una.log.
    """

    ruta_datos = Path(ruta_datos)
    ruta_datos.mkdir(parents=True, exist_ok=True)

    ruta_log = (ruta_datos / "social_una.log").resolve()

    # Un registrador independiente para cada ruta de datos.
    nombre = f"social_una.eventos.{ruta_log}"
    logger = logging.getLogger(nombre)

    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Evitar crear varios manejadores para el mismo archivo.
    if not logger.handlers:
        manejador = logging.FileHandler(
            ruta_log,
            encoding="utf-8",
        )

        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        manejador.setFormatter(formato)
        logger.addHandler(manejador)

    return logger
