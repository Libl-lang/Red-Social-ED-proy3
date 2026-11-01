"""
Lectura y escritura segura de archivos JSON.

Lo usan los tres repositorios (usuarios, amistades y publicaciones) para
guardar y cargar los datos. No decide cuándo guardar, solo cómo hacerlo.
"""

import json
import os
from pathlib import Path
from typing import Any

from ..dominio.errores import ErrorAlmacenamiento


class AlmacenJson:
    """
    Lee y escribe archivos JSON.

    La escritura es segura: primero se escribe en un archivo temporal (.tmp) y,
    solo cuando termina bien, reemplaza al original. Así un cierre inesperado
    no deja el archivo cortado. Lanza ErrorAlmacenamiento si hay problemas.
    """

    def leer(self, ruta: str | Path, valor_por_defecto: Any) -> Any:
        """
        Lee un archivo JSON y devuelve su contenido como datos de Python.

        Recibe la ruta del archivo y el valor que se devuelve si el archivo no
        existe (por ejemplo, una lista vacía). Un archivo vacío (0 bytes) se
        considera dañado. Lanza ErrorAlmacenamiento si no se puede leer.
        """
        # 1) Convierte la ruta a Path
        ruta_archivo = Path(ruta)

        # 2) Si no existe, devuelve el valor por defecto (la app arranca vacía)
        if not ruta_archivo.exists():
            return valor_por_defecto

        # 3) Si existe, lo abre y lo convierte a datos de Python
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        # 4) Si está dañado o no se puede abrir, lanza un error de negocio
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            raise ErrorAlmacenamiento(
                f"No se pudo leer el archivo {ruta}: está dañado o no se puede abrir."
            )

    def escribir_seguro(self, ruta: str | Path, datos: Any) -> None:
        """
        Guarda datos en un archivo JSON sin arriesgar el original.

        Recibe la ruta del archivo y los datos a guardar. Escribe primero en un
        archivo temporal (por ejemplo usuarios.json.tmp, en la misma carpeta) y,
        al terminar, lo reemplaza sobre el original. Si algo falla, el original
        no se toca y se lanza ErrorAlmacenamiento.
        """
        # 1) Convierte la ruta a Path y define el archivo temporal
        ruta_archivo = Path(ruta)
        ruta_temporal = ruta_archivo.with_name(ruta_archivo.name + ".tmp")

        try:
            # 2) Crea la carpeta si no existe
            ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

            # 3) Escribe los datos en el archivo temporal
            with open(ruta_temporal, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
                # 4) Fuerza que los datos queden realmente en el disco
                archivo.flush()
                os.fsync(archivo.fileno())

            # 5) Solo si todo salió bien, reemplaza el original
            os.replace(ruta_temporal, ruta_archivo)
        except (OSError, TypeError):
            # 6) Si falla, borra el temporal y deja intacto el original
            if ruta_temporal.exists():
                try:
                    ruta_temporal.unlink()
                except OSError:
                    pass
            raise ErrorAlmacenamiento(f"No se pudo guardar el archivo {ruta}.")