"""Pieza falsa para DirectorioUsuarios.

Proporciona datos fijos y comportamientos simulados para las pruebas unitarias.
No tiene lógica de negocio real, solo devuelve datos predefinidos."""

import unicodedata
from social_una.dominio.contratos import DirectorioUsuarios
from social_una.dominio.errores import ErrorNoEncontrado
from social_una.dominio.modelos import Usuario

USUARIOS_FALSOS = [
    Usuario(id_usuario=1, nombre="Ana Mora", nombre_usuario="ana",
            hash_contrasena="hash_falso_1", sal="sal_falsa_1",
            fecha_registro="2026-11-01T08:00:00+00:00"),
    Usuario(id_usuario=2, nombre="Beto Rojas", nombre_usuario="beto",
            hash_contrasena="hash_falso_2", sal="sal_falsa_2",
            fecha_registro="2026-11-01T08:05:00+00:00"),
    Usuario(id_usuario=3, nombre="Carla Vega", nombre_usuario="carla",
            hash_contrasena="hash_falso_3", sal="sal_falsa_3",
            fecha_registro="2026-11-01T08:10:00+00:00"),
]


def _normalizar(texto: str) -> str:
    """Normaliza un texto quitando tildes y poniendo en minúsculas."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.combining(c) == 0)


class DirectorioUsuariosFalso(DirectorioUsuarios):
    """Implementación falsa de DirectorioUsuarios para pruebas."""

    def obtener_por_id(self, id_usuario: int) -> Usuario:
        """Devuelve el usuario de USUARIOS_FALSOS con ese id; si no existe,
        lanza ErrorNoEncontrado."""
        for u in USUARIOS_FALSOS:
            if u.id_usuario == id_usuario:
                return u
        raise ErrorNoEncontrado(f"No existe el usuario con id {id_usuario}.")

    def buscar(self, texto: str) -> list[Usuario]:
        """Si el texto está vacío devuelve []. Devuelve los usuarios cuyo
        nombre o nombre_usuario, normalizados, contienen el texto normalizado;
        el resultado ordenado por nombre normalizado."""
        if texto.strip() == "":
            return []
        texto_norm = _normalizar(texto)
        resultado = [
            u for u in USUARIOS_FALSOS
            if _normalizar(u.nombre).find(texto_norm) != -1
            or _normalizar(u.nombre_usuario).find(texto_norm) != -1
        ]
        return sorted(resultado, key=lambda u: _normalizar(u.nombre))

    def existe(self, id_usuario: int) -> bool:
        """True si hay un usuario con ese id."""
        return any(u.id_usuario == id_usuario for u in USUARIOS_FALSOS)
