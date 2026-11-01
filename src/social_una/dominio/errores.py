"""Errores de negocio de Social UNA.

Estas excepciones representan situaciones en las que una operación no se puede
realizar en el dominio de la aplicación. Los servicios las lanzan con un mensaje
cuando se detecta un problema. La interfaz atrapa estas excepciones y
las muestra como alertas gráficas al usuario.

Todas estas clases heredan de ErrorSocialUna."""

class ErrorSocialUna(Exception):
    """Excepción base para todos los errores de negocio de Social UNA."""

class ErrorValidacion(ErrorSocialUna):
    """Dato inválido: campo vacío, texto demasiado largo, contraseña muy corta, agregar a uno mismo como amigo."""

class ErrorDuplicado(ErrorSocialUna):
    """Se intentó crear algo que ya existe: usuario repetido, amistad repetida."""

class ErrorNoEncontrado(ErrorSocialUna):
    """Se buscó algo que no existe: usuario con un id inexistente."""

class ErrorAutenticacion(ErrorSocialUna):
    """Credenciales inválidas al iniciar sesión."""

class ErrorAlmacenamiento(ErrorSocialUna):
    """Un archivo de datos no se pudo leer o está corrupto."""

