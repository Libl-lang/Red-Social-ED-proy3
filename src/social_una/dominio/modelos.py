"""
Modelos del dominio de Social UNA.

Este archivo define los datos puros del sistema: Usuario y Publicacion.
No tiene lógica de archivos, ventanas ni validaciones; eso lo hacen los
servicios, los repositorios y la interfaz.
"""

from dataclasses import dataclass


@dataclass
class Usuario:
    """
    Representa a una persona registrada en la red social.

    Se crea al registrarse y se guarda en usuarios.json. Guarda el hash de la
    contraseña y su sal, nunca la contraseña original. Lo usan los tres módulos:
    M1 para registrar e iniciar sesión, M2 para las amistades y M3 para mostrar
    el nombre del autor de cada publicación.
    """

    id_usuario: int        # Identificador único; entero desde 1
    nombre: str            # Nombre completo, por ejemplo "Ana Mora"
    nombre_usuario: str    # Nombre con el que inicia sesión; no se puede repetir
    hash_contrasena: str   # Hash de la contraseña; nunca se guarda en texto plano
    sal: str               # Texto aleatorio usado para calcular el hash
    fecha_registro: str    # Fecha en texto ISO 8601, por ejemplo "2026-11-03T14:30:00+00:00"

    def a_diccionario(self) -> dict:
        # Convierte el usuario en un diccionario listo para guardar en JSON.
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "nombre_usuario": self.nombre_usuario,
            "hash_contrasena": self.hash_contrasena,
            "sal": self.sal,
            "fecha_registro": self.fecha_registro,
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Usuario":
        # Reconstruye un Usuario desde un diccionario; el id vuelve siempre como entero.
        return cls(
            id_usuario=int(datos["id_usuario"]),
            nombre=datos["nombre"],
            nombre_usuario=datos["nombre_usuario"],
            hash_contrasena=datos["hash_contrasena"],
            sal=datos["sal"],
            fecha_registro=datos["fecha_registro"],
        )


@dataclass
class Publicacion:
    """
    Representa un mensaje que un usuario publica en el muro.

    Se guarda en publicaciones.json. Cada publicación apunta a su autor por id
    (id_autor), no guarda el objeto Usuario completo. El muro de un usuario se
    arma con las publicaciones suyas y de sus amigos, ordenadas de la más
    reciente a la más antigua.
    """

    id_publicacion: int    # Identificador único de la publicación; entero desde 1
    id_autor: int          # Id del Usuario que la escribió
    texto: str             # Contenido del mensaje (máximo 280 caracteres)
    fecha_creacion: str    # Fecha en texto ISO 8601, por ejemplo "2026-11-03T14:30:00+00:00"

    def a_diccionario(self) -> dict:
        # Convierte la publicación en un diccionario listo para guardar en JSON.
        return {
            "id_publicacion": self.id_publicacion,
            "id_autor": self.id_autor,
            "texto": self.texto,
            "fecha_creacion": self.fecha_creacion,
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Publicacion":
        # Reconstruye una Publicacion desde un diccionario; los ids vuelven siempre como enteros.
        return cls(
            id_publicacion=int(datos["id_publicacion"]),
            id_autor=int(datos["id_autor"]),
            texto=datos["texto"],
            fecha_creacion=datos["fecha_creacion"],
        )