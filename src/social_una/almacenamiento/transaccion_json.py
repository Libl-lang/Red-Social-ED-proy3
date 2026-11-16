"""Persistencia recuperable para operaciones que modifican varios JSON."""

import hashlib
import json
import logging
import os
from pathlib import Path
import uuid

from social_una.dominio.errores import (
    ErrorAlmacenamiento,
    ErrorRecuperacionTransaccion,
)


_ARCHIVO_DIARIO = ".social_una_transaccion.json"
_ARCHIVOS_CUENTA = {
    "usuarios.json",
    "amistades.json",
    "publicaciones.json",
}
_REGISTRADOR = logging.getLogger(__name__)


def guardar_json_transaccional(
    directorio: str | Path,
    actualizaciones: dict[str, object],
) -> None:
    """Reemplaza los tres archivos JSON con diario y respaldos recuperables.

    Los cambios individuales usan reemplazos atómicos. El conjunto no es una
    única operación atómica: el diario permite revertir un estado preparado al
    iniciar la aplicación si el proceso se interrumpe entre reemplazos.
    """
    carpeta = Path(directorio)
    if set(actualizaciones) != _ARCHIVOS_CUENTA:
        raise ErrorAlmacenamiento(
            "La transacción de cuenta requiere los tres archivos JSON."
        )

    carpeta.mkdir(parents=True, exist_ok=True)
    diario = carpeta / _ARCHIVO_DIARIO
    recuperar_transaccion_json(carpeta)
    if diario.exists():
        raise ErrorAlmacenamiento(
            "Hay una transacción anterior pendiente de recuperación."
        )

    identificador = uuid.uuid4().hex
    registros = []
    originales: dict[str, bytes | None] = {}
    nuevos: dict[str, bytes] = {}

    try:
        for nombre in sorted(_ARCHIVOS_CUENTA):
            ruta = carpeta / nombre
            original = ruta.read_bytes() if ruta.exists() else None
            contenido = json.dumps(
                actualizaciones[nombre],
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8")
            originales[nombre] = original
            nuevos[nombre] = contenido
            registros.append(
                {
                    "target": nombre,
                    "backup": _nombre_respaldo(identificador, nombre),
                    "staged": _nombre_nuevo(identificador, nombre),
                    "existed": original is not None,
                    "sha256": (
                        hashlib.sha256(original).hexdigest()
                        if original is not None
                        else None
                    ),
                }
            )
    except (OSError, TypeError, ValueError) as error:
        raise ErrorAlmacenamiento(
            "No se pudieron leer o preparar los datos para guardar la cuenta."
        ) from error

    manifiesto = {
        "version": 1,
        "id": identificador,
        "state": "staging",
        "files": registros,
    }

    try:
        _escribir_diario_nuevo(diario, manifiesto)
        for registro in registros:
            original = originales[registro["target"]]
            if original is not None:
                _escribir_durable(
                    carpeta / registro["backup"],
                    original,
                    exclusivo=True,
                )
            _escribir_durable(
                carpeta / registro["staged"],
                nuevos[registro["target"]],
                exclusivo=True,
            )
        manifiesto["state"] = "prepared"
        _actualizar_diario(diario, manifiesto)
    except OSError as error:
        try:
            recuperar_transaccion_json(carpeta)
        except ErrorAlmacenamiento as recuperacion:
            raise ErrorRecuperacionTransaccion(
                "No se pudieron preparar ni limpiar los archivos temporales. "
                "Reinicia la aplicación para reintentar la recuperación."
            ) from recuperacion
        raise ErrorAlmacenamiento(
            "No se pudieron preparar los archivos para eliminar la cuenta."
        ) from error

    try:
        for registro in registros:
            os.replace(
                carpeta / registro["staged"],
                carpeta / registro["target"],
            )
        manifiesto["state"] = "committed"
        _actualizar_diario(diario, manifiesto)
    except OSError as error:
        try:
            _restaurar_originales(carpeta, manifiesto)
            manifiesto["state"] = "rolled_back"
            _actualizar_diario(diario, manifiesto)
            _limpiar_transaccion(carpeta, manifiesto)
        except OSError as recuperacion:
            raise ErrorRecuperacionTransaccion(
                "Falló una escritura y no se pudo completar la recuperación. "
                "Cierra y reinicia la aplicación para reintentarla."
            ) from recuperacion
        raise ErrorAlmacenamiento(
            "No se pudieron guardar juntos los datos de la cuenta; "
            "se restauraron los archivos originales."
        ) from error

    _limpiar_transaccion(carpeta, manifiesto, informar_error=True)


def recuperar_transaccion_json(directorio: str | Path) -> None:
    """Recupera o limpia una transacción pendiente antes de cargar servicios."""
    carpeta = Path(directorio)
    diario = carpeta / _ARCHIVO_DIARIO
    if not diario.exists():
        try:
            diario.with_name(diario.name + ".tmp").unlink(missing_ok=True)
        except OSError as error:
            raise ErrorRecuperacionTransaccion(
                "No se pudo limpiar el archivo temporal del diario JSON."
            ) from error
        return

    try:
        with diario.open("r", encoding="utf-8") as archivo:
            manifiesto = json.load(archivo)
        _validar_manifiesto(manifiesto)
        if manifiesto["state"] == "prepared":
            _restaurar_originales(carpeta, manifiesto)
            manifiesto["state"] = "rolled_back"
            _actualizar_diario(diario, manifiesto)
        _limpiar_transaccion(carpeta, manifiesto)
    except ErrorAlmacenamiento:
        raise
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, TypeError, KeyError) as error:
        raise ErrorRecuperacionTransaccion(
            "No se pudo leer o recuperar la transacción JSON pendiente."
        ) from error


def _nombre_respaldo(identificador: str, nombre: str) -> str:
    return f".social-una-{identificador}-{nombre}.respaldo"


def _nombre_nuevo(identificador: str, nombre: str) -> str:
    return f".social-una-{identificador}-{nombre}.nuevo"


def _escribir_durable(
    ruta: Path,
    contenido: bytes,
    *,
    exclusivo: bool = False,
) -> None:
    modo = "xb" if exclusivo else "wb"
    with ruta.open(modo) as archivo:
        archivo.write(contenido)
        archivo.flush()
        os.fsync(archivo.fileno())


def _escribir_diario_nuevo(ruta: Path, manifiesto: dict) -> None:
    contenido = json.dumps(manifiesto, ensure_ascii=True).encode("utf-8")
    temporal = ruta.with_name(ruta.name + ".tmp")
    _escribir_durable(temporal, contenido, exclusivo=True)
    os.replace(temporal, ruta)


def _actualizar_diario(ruta: Path, manifiesto: dict) -> None:
    temporal = ruta.with_name(ruta.name + ".tmp")
    contenido = json.dumps(manifiesto, ensure_ascii=True).encode("utf-8")
    _escribir_durable(temporal, contenido)
    os.replace(temporal, ruta)


def _validar_manifiesto(manifiesto: object) -> None:
    if not isinstance(manifiesto, dict):
        raise ErrorRecuperacionTransaccion("El diario de transacción es inválido.")
    if (
        manifiesto.get("version") != 1
        or manifiesto.get("state")
        not in {"staging", "prepared", "committed", "rolled_back"}
        or not isinstance(manifiesto.get("id"), str)
        or len(manifiesto["id"]) != 32
        or any(caracter not in "0123456789abcdef" for caracter in manifiesto["id"])
        or not isinstance(manifiesto.get("files"), list)
    ):
        raise ErrorRecuperacionTransaccion("El diario de transacción es inválido.")

    archivos = manifiesto["files"]
    nombres = {registro.get("target") for registro in archivos if isinstance(registro, dict)}
    if nombres != _ARCHIVOS_CUENTA or len(archivos) != len(_ARCHIVOS_CUENTA):
        raise ErrorRecuperacionTransaccion(
            "El diario no contiene exactamente los archivos de cuenta esperados."
        )

    for registro in archivos:
        nombre = registro["target"]
        if (
            registro.get("backup") != _nombre_respaldo(manifiesto["id"], nombre)
            or registro.get("staged") != _nombre_nuevo(manifiesto["id"], nombre)
            or not isinstance(registro.get("existed"), bool)
            or (
                registro["existed"]
                and (
                    not isinstance(registro.get("sha256"), str)
                    or len(registro["sha256"]) != 64
                    or any(
                        caracter not in "0123456789abcdef"
                        for caracter in registro["sha256"]
                    )
                )
            )
            or (
                not registro["existed"]
                and registro.get("sha256") is not None
            )
        ):
            raise ErrorRecuperacionTransaccion(
                "El diario contiene rutas de recuperación inválidas."
            )


def _restaurar_originales(carpeta: Path, manifiesto: dict) -> None:
    registros = manifiesto["files"]
    for registro in registros:
        if not registro["existed"]:
            continue
        respaldo = carpeta / registro["backup"]
        try:
            contenido = respaldo.read_bytes()
        except OSError as error:
            raise OSError(
                f"No se puede leer el respaldo de {registro['target']}."
            ) from error
        if hashlib.sha256(contenido).hexdigest() != registro["sha256"]:
            raise OSError(
                f"El respaldo de {registro['target']} no coincide con su huella."
            )

    for registro in reversed(registros):
        destino = carpeta / registro["target"]
        if registro["existed"]:
            respaldo = carpeta / registro["backup"]
            temporal = carpeta / (registro["backup"] + ".restaurar")
            _escribir_durable(temporal, respaldo.read_bytes())
            os.replace(temporal, destino)
        else:
            destino.unlink(missing_ok=True)


def _limpiar_transaccion(
    carpeta: Path,
    manifiesto: dict,
    *,
    informar_error: bool = False,
) -> None:
    errores = []
    for registro in manifiesto["files"]:
        for nombre in (
            registro["staged"],
            registro["backup"],
            registro["backup"] + ".restaurar",
        ):
            try:
                (carpeta / nombre).unlink(missing_ok=True)
            except OSError as error:
                errores.append(error)

    if errores:
        if informar_error:
            _REGISTRADOR.warning(
                "La transacción JSON terminó, pero no se pudieron limpiar "
                "todos sus archivos auxiliares."
            )
            return
        raise errores[0]

    diario = carpeta / _ARCHIVO_DIARIO
    try:
        diario.unlink(missing_ok=True)
    except OSError as error:
        errores.append(error)

    temporal_diario = diario.with_name(diario.name + ".tmp")
    try:
        temporal_diario.unlink(missing_ok=True)
    except OSError as error:
        errores.append(error)

    if errores:
        if informar_error:
            _REGISTRADOR.warning(
                "La transacción JSON terminó, pero no se pudo retirar "
                "el diario auxiliar."
            )
            return
        raise errores[0]
