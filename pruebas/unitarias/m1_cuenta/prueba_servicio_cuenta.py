"""Pruebas de eliminación de cuenta sobre archivos temporales."""

import hashlib
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from social_una.almacenamiento.almacen_json import AlmacenJson
from social_una.almacenamiento.repositorio_amistades_json import (
    RepositorioAmistadesJson,
)
from social_una.almacenamiento.repositorio_publicaciones_json import (
    RepositorioPublicacionesJson,
)
from social_una.almacenamiento.repositorio_usuarios_json import (
    RepositorioUsuariosJson,
)
from social_una.almacenamiento.transaccion_json import (
    guardar_json_transaccional,
)
from social_una.composicion import construir_aplicacion
from social_una.dominio.errores import (
    ErrorAlmacenamiento,
    ErrorAutenticacion,
    ErrorNoEncontrado,
    ErrorRecuperacionTransaccion,
    ErrorValidacion,
)
from social_una.dominio.modelos import Publicacion, Usuario
from social_una.interfaz import vista_perfil
from social_una.interfaz import ventana_principal
from social_una.interfaz.vista_perfil import VistaPerfil
from social_una.servicios.servicio_autenticacion import ServicioAutenticacion
from social_una.servicios.servicio_cuenta import ServicioCuenta
from social_una.servicios.servicio_publicaciones import ServicioPublicaciones
from social_una.servicios.servicio_social import ServicioSocial
from social_una.servicios.sesion import Sesion


_CONTRASENA = "clave-segura-123"
_ARCHIVOS = ("usuarios.json", "amistades.json", "publicaciones.json")


def _crear_usuario(id_usuario: int) -> Usuario:
    sal = f"sal-de-prueba-{id_usuario}"
    hash_contrasena = hashlib.pbkdf2_hmac(
        "sha256",
        _CONTRASENA.encode("utf-8"),
        sal.encode("utf-8"),
        ServicioAutenticacion.ITERACIONES_HASH,
    ).hex()
    return Usuario(
        id_usuario=id_usuario,
        nombre=f"Persona de prueba {id_usuario}",
        nombre_usuario=f"persona{id_usuario}",
        hash_contrasena=hash_contrasena,
        sal=sal,
        fecha_registro="2026-01-02T03:04:05+00:00",
    )


def _crear_contexto(directorio: Path):
    repo_usuarios = RepositorioUsuariosJson(
        AlmacenJson(),
        directorio / "usuarios.json",
    )
    repo_amistades = RepositorioAmistadesJson(
        directorio / "amistades.json"
    )
    repo_publicaciones = RepositorioPublicacionesJson(
        directorio / "publicaciones.json",
        AlmacenJson(),
    )
    usuarios = [_crear_usuario(id_usuario) for id_usuario in range(1, 5)]
    amistades = [(1, 2), (1, 3), (2, 3), (3, 4)]
    publicaciones = [
        Publicacion(1, 1, "Publicación de otra persona", "2026-01-01"),
        Publicacion(2, 2, "Publicación propia", "2026-01-02"),
        Publicacion(3, 3, "Otra publicación ajena", "2026-01-03"),
    ]
    repo_usuarios.guardar_todo(usuarios)
    repo_amistades.guardar_todo(amistades)
    repo_publicaciones.guardar_todo(publicaciones)

    sesion = Sesion()
    autenticacion = ServicioAutenticacion(repo_usuarios, sesion)
    autenticacion.iniciar_sesion("persona2", _CONTRASENA)
    social = ServicioSocial(repo_amistades, autenticacion, sesion)
    servicio_publicaciones = ServicioPublicaciones(
        repo_publicaciones,
        social,
        autenticacion,
        sesion,
    )
    servicio_cuenta = ServicioCuenta(
        directorio,
        repo_usuarios,
        repo_amistades,
        repo_publicaciones,
        autenticacion,
        social,
        servicio_publicaciones,
        sesion,
    )
    return SimpleNamespace(
        repositorio_usuarios=repo_usuarios,
        repositorio_amistades=repo_amistades,
        repositorio_publicaciones=repo_publicaciones,
        sesion=sesion,
        autenticacion=autenticacion,
        social=social,
        publicaciones=servicio_publicaciones,
        cuenta=servicio_cuenta,
    )


def _bytes_archivos(directorio: Path) -> dict[str, bytes]:
    return {
        nombre: (directorio / nombre).read_bytes()
        for nombre in _ARCHIVOS
    }


def prueba_eliminar_cuenta_borra_datos_relacionados_y_conserva_terceros(
    tmp_path,
):
    contexto = _crear_contexto(tmp_path)

    contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)

    assert [
        usuario.id_usuario
        for usuario in contexto.repositorio_usuarios.cargar_todo()
    ] == [1, 3, 4]
    assert contexto.repositorio_amistades.cargar_todo() == [(1, 3), (3, 4)]
    assert [
        publicacion.id_publicacion
        for publicacion in contexto.repositorio_publicaciones.cargar_todo()
    ] == [1, 3]
    assert contexto.social.son_amigos(1, 3)
    assert contexto.social.son_amigos(3, 4)
    assert not contexto.social.son_amigos(1, 2)
    assert [
        publicacion.id_publicacion
        for publicacion in contexto.publicaciones._historial.listar_todas()
    ] == [1, 3]
    assert not contexto.sesion.hay_sesion_iniciada()
    with pytest.raises(ErrorNoEncontrado):
        contexto.autenticacion.obtener_por_id(2)


def prueba_contrasena_incorrecta_no_modifica_archivos_ni_sesion(tmp_path):
    contexto = _crear_contexto(tmp_path)
    antes = _bytes_archivos(tmp_path)

    with pytest.raises(ErrorAutenticacion, match="incorrecta"):
        contexto.cuenta.eliminar_mi_cuenta("incorrecta")

    assert _bytes_archivos(tmp_path) == antes
    assert contexto.sesion.hay_sesion_iniciada()


def prueba_sesion_no_iniciada_no_elimina_datos(tmp_path):
    contexto = _crear_contexto(tmp_path)
    contexto.sesion.cerrar()
    antes = _bytes_archivos(tmp_path)

    with pytest.raises(ErrorAutenticacion, match="sesion iniciada"):
        contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)

    assert _bytes_archivos(tmp_path) == antes


def prueba_usuario_que_ya_no_esta_en_repositorio_no_se_elimina(tmp_path):
    contexto = _crear_contexto(tmp_path)
    contexto.repositorio_usuarios.guardar_todo(
        [
            usuario
            for usuario in contexto.repositorio_usuarios.cargar_todo()
            if usuario.id_usuario != 2
        ]
    )
    amistades_antes = (tmp_path / "amistades.json").read_bytes()
    publicaciones_antes = (tmp_path / "publicaciones.json").read_bytes()

    with pytest.raises(ErrorNoEncontrado, match="ya no existe"):
        contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)

    assert (tmp_path / "amistades.json").read_bytes() == amistades_antes
    assert (tmp_path / "publicaciones.json").read_bytes() == publicaciones_antes


def prueba_error_de_lectura_no_inicia_ninguna_escritura(tmp_path):
    contexto = _crear_contexto(tmp_path)
    amistades_antes = (tmp_path / "amistades.json").read_bytes()
    (tmp_path / "publicaciones.json").write_text("{ roto", encoding="utf-8")

    with pytest.raises(ErrorAlmacenamiento):
        contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)

    assert (tmp_path / "amistades.json").read_bytes() == amistades_antes
    assert contexto.sesion.hay_sesion_iniciada()


def prueba_fallo_en_tercera_escritura_revierte_todos_los_archivos(
    tmp_path,
    monkeypatch,
):
    contexto = _crear_contexto(tmp_path)
    antes = _bytes_archivos(tmp_path)
    reemplazar_real = os.replace
    fallo_inyectado = False

    def reemplazar_con_fallo_una_vez(origen, destino):
        nonlocal fallo_inyectado
        if (
            Path(destino).name == "usuarios.json"
            and Path(origen).name.endswith(".nuevo")
            and not fallo_inyectado
        ):
            fallo_inyectado = True
            raise PermissionError("fallo simulado")
        reemplazar_real(origen, destino)

    monkeypatch.setattr(
        "social_una.almacenamiento.transaccion_json.os.replace",
        reemplazar_con_fallo_una_vez,
    )

    with pytest.raises(ErrorAlmacenamiento, match="restauraron"):
        contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)

    assert fallo_inyectado
    assert _bytes_archivos(tmp_path) == antes
    assert not (tmp_path / ".social_una_transaccion.json").exists()
    assert contexto.sesion.hay_sesion_iniciada()


def prueba_reinicio_recupera_transaccion_interrumpida(tmp_path, monkeypatch):
    contexto = _crear_contexto(tmp_path)
    antes = _bytes_archivos(tmp_path)
    actualizaciones = {
        "usuarios.json": [
            usuario.a_diccionario()
            for usuario in contexto.repositorio_usuarios.cargar_todo()
            if usuario.id_usuario != 2
        ],
        "amistades.json": [[1, 3], [3, 4]],
        "publicaciones.json": [
            publicacion.a_diccionario()
            for publicacion in contexto.repositorio_publicaciones.cargar_todo()
            if publicacion.id_autor != 2
        ],
    }
    reemplazar_real = os.replace

    def interrumpir_tras_primer_archivo(origen, destino):
        if (
            Path(destino).name == "publicaciones.json"
            and Path(origen).name.endswith(".nuevo")
        ):
            raise KeyboardInterrupt
        reemplazar_real(origen, destino)

    monkeypatch.setattr(
        "social_una.almacenamiento.transaccion_json.os.replace",
        interrumpir_tras_primer_archivo,
    )
    with pytest.raises(KeyboardInterrupt):
        guardar_json_transaccional(tmp_path, actualizaciones)

    assert (tmp_path / ".social_una_transaccion.json").exists()
    monkeypatch.setattr(
        "social_una.almacenamiento.transaccion_json.os.replace",
        reemplazar_real,
    )
    aplicacion = construir_aplicacion(tmp_path)

    assert _bytes_archivos(tmp_path) == antes
    assert not (tmp_path / ".social_una_transaccion.json").exists()
    assert sorted(
        usuario.id_usuario
        for usuario in aplicacion["repositorio_usuarios"].cargar_todo()
    ) == [1, 2, 3, 4]
    for handler in aplicacion["registrador"].handlers:
        handler.close()


def prueba_reinicio_recupera_si_tambien_falla_el_rollback(tmp_path, monkeypatch):
    contexto = _crear_contexto(tmp_path)
    antes = _bytes_archivos(tmp_path)
    reemplazar_real = os.replace
    fallo_commit = False
    fallo_rollback = False

    def fallar_commit_y_rollback(origen, destino):
        nonlocal fallo_commit, fallo_rollback
        nombre_origen = Path(origen).name
        nombre_destino = Path(destino).name
        if (
            nombre_destino == "usuarios.json"
            and nombre_origen.endswith(".nuevo")
            and not fallo_commit
        ):
            fallo_commit = True
            raise PermissionError("fallo de escritura simulado")
        if (
            nombre_destino == "usuarios.json"
            and nombre_origen.endswith(".respaldo.restaurar")
            and not fallo_rollback
        ):
            fallo_rollback = True
            raise PermissionError("fallo de recuperación simulado")
        reemplazar_real(origen, destino)

    monkeypatch.setattr(
        "social_una.almacenamiento.transaccion_json.os.replace",
        fallar_commit_y_rollback,
    )
    with pytest.raises(ErrorRecuperacionTransaccion):
        contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)

    assert fallo_commit and fallo_rollback
    assert (tmp_path / ".social_una_transaccion.json").exists()
    monkeypatch.setattr(
        "social_una.almacenamiento.transaccion_json.os.replace",
        reemplazar_real,
    )
    aplicacion = construir_aplicacion(tmp_path)

    assert _bytes_archivos(tmp_path) == antes
    assert sorted(
        usuario.id_usuario
        for usuario in aplicacion["repositorio_usuarios"].cargar_todo()
    ) == [1, 2, 3, 4]
    for handler in aplicacion["registrador"].handlers:
        handler.close()


def prueba_recarga_desde_archivos_confirma_eliminacion_persistida(tmp_path):
    contexto = _crear_contexto(tmp_path)
    contexto.cuenta.eliminar_mi_cuenta(_CONTRASENA)
    aplicacion = construir_aplicacion(tmp_path)

    usuarios_recargados = RepositorioUsuariosJson(
        AlmacenJson(),
        tmp_path / "usuarios.json",
    ).cargar_todo()
    amistades_recargadas = RepositorioAmistadesJson(
        tmp_path / "amistades.json"
    ).cargar_todo()
    publicaciones_recargadas = RepositorioPublicacionesJson(
        tmp_path / "publicaciones.json",
        AlmacenJson(),
    ).cargar_todo()

    assert [usuario.id_usuario for usuario in usuarios_recargados] == [1, 3, 4]
    assert amistades_recargadas == [(1, 3), (3, 4)]
    assert [publicacion.id_publicacion for publicacion in publicaciones_recargadas] == [1, 3]
    assert not aplicacion["autenticacion"].existe(2)
    assert aplicacion["social"].son_amigos(1, 3)
    assert [
        publicacion.id_publicacion
        for publicacion in aplicacion["publicaciones"]._historial.listar_todas()
    ] == [1, 3]
    for handler in aplicacion["registrador"].handlers:
        handler.close()


def prueba_cancelacion_en_dialogo_no_invoca_eliminacion(monkeypatch):
    eliminaciones = []
    clase_boton = SimpleNamespace(configure=lambda **_kwargs: None)
    vista = SimpleNamespace(
        _eliminando=False,
        _boton_eliminar=clase_boton,
        winfo_toplevel=lambda: object(),
        winfo_exists=lambda: True,
        _autenticacion=SimpleNamespace(
            verificar_contrasena_actual=lambda _password: pytest.fail(
                "No se debe verificar una contraseña al cancelar"
            )
        ),
        _servicio_cuenta=SimpleNamespace(
            eliminar_mi_cuenta=lambda password: eliminaciones.append(password)
        ),
        _al_eliminar_cuenta=lambda: pytest.fail(
            "La cancelación no debe completar el flujo"
        ),
        _al_fallo_recuperacion=lambda _mensaje: None,
    )
    monkeypatch.setattr(vista_perfil.messagebox, "askyesno", lambda *a, **k: False)

    VistaPerfil._solicitar_eliminacion(vista)

    assert eliminaciones == []
    assert vista._eliminando is False


def prueba_cancelar_ingreso_de_contrasena_no_modifica_datos(monkeypatch):
    verificaciones = []
    vista = SimpleNamespace(
        _eliminando=False,
        _boton_eliminar=SimpleNamespace(configure=lambda **_kwargs: None),
        winfo_toplevel=lambda: object(),
        winfo_exists=lambda: True,
        _autenticacion=SimpleNamespace(
            verificar_contrasena_actual=lambda password: verificaciones.append(
                password
            )
        ),
        _servicio_cuenta=SimpleNamespace(
            eliminar_mi_cuenta=lambda _password: pytest.fail(
                "No se debe eliminar si el diálogo de contraseña se cancela"
            )
        ),
        _al_eliminar_cuenta=lambda: pytest.fail(
            "La cancelación no debe terminar el flujo"
        ),
        _al_fallo_recuperacion=lambda _mensaje: None,
    )
    confirmaciones = iter((True,))
    monkeypatch.setattr(
        vista_perfil.messagebox,
        "askyesno",
        lambda *args, **kwargs: next(confirmaciones),
    )
    monkeypatch.setattr(
        vista_perfil.simpledialog,
        "askstring",
        lambda *args, **kwargs: None,
    )

    VistaPerfil._solicitar_eliminacion(vista)

    assert verificaciones == []
    assert vista._eliminando is False


def prueba_cancelar_confirmacion_final_no_modifica_datos(monkeypatch):
    verificaciones = []
    eliminaciones = []
    vista = SimpleNamespace(
        _eliminando=False,
        _boton_eliminar=SimpleNamespace(configure=lambda **_kwargs: None),
        winfo_toplevel=lambda: object(),
        winfo_exists=lambda: True,
        _autenticacion=SimpleNamespace(
            verificar_contrasena_actual=lambda password: verificaciones.append(
                password
            )
        ),
        _servicio_cuenta=SimpleNamespace(
            eliminar_mi_cuenta=lambda password: eliminaciones.append(password)
        ),
        _al_eliminar_cuenta=lambda: pytest.fail(
            "No debe finalizarse si se cancela la última confirmación"
        ),
        _al_fallo_recuperacion=lambda _mensaje: None,
    )
    confirmaciones = iter((True, False))
    monkeypatch.setattr(
        vista_perfil.messagebox,
        "askyesno",
        lambda *args, **kwargs: next(confirmaciones),
    )
    monkeypatch.setattr(
        vista_perfil.simpledialog,
        "askstring",
        lambda *args, **kwargs: _CONTRASENA,
    )

    VistaPerfil._solicitar_eliminacion(vista)

    assert verificaciones == [_CONTRASENA]
    assert eliminaciones == []


def prueba_contrasena_incorrecta_muestra_error_y_no_elimina(monkeypatch):
    errores = []
    eliminaciones = []
    vista = SimpleNamespace(
        _eliminando=False,
        _boton_eliminar=SimpleNamespace(configure=lambda **_kwargs: None),
        winfo_toplevel=lambda: object(),
        winfo_exists=lambda: True,
        _autenticacion=SimpleNamespace(
            verificar_contrasena_actual=lambda _password: (_ for _ in ()).throw(
                ErrorAutenticacion("La contraseña actual es incorrecta.")
            )
        ),
        _servicio_cuenta=SimpleNamespace(
            eliminar_mi_cuenta=lambda password: eliminaciones.append(password)
        ),
        _al_eliminar_cuenta=lambda: None,
        _al_fallo_recuperacion=lambda _mensaje: None,
    )
    monkeypatch.setattr(vista_perfil.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(
        vista_perfil.simpledialog,
        "askstring",
        lambda *a, **k: _CONTRASENA,
    )
    monkeypatch.setattr(
        vista_perfil.messagebox,
        "showerror",
        lambda _title, message, **_kwargs: errores.append(message),
    )

    VistaPerfil._solicitar_eliminacion(vista)

    assert errores == ["La contraseña actual es incorrecta."]
    assert eliminaciones == []


def prueba_confirmacion_final_elimina_y_cierra_sesion(monkeypatch, tmp_path):
    contexto = _crear_contexto(tmp_path)
    confirmaciones = iter((True, True))
    completadas = []
    vista = SimpleNamespace(
        _eliminando=False,
        _boton_eliminar=SimpleNamespace(configure=lambda **_kwargs: None),
        winfo_toplevel=lambda: object(),
        winfo_exists=lambda: True,
        _autenticacion=contexto.autenticacion,
        _servicio_cuenta=contexto.cuenta,
        _al_eliminar_cuenta=lambda: completadas.append(True),
        _al_fallo_recuperacion=lambda mensaje: pytest.fail(mensaje),
    )
    monkeypatch.setattr(
        vista_perfil.messagebox,
        "askyesno",
        lambda *a, **k: next(confirmaciones),
    )
    monkeypatch.setattr(
        vista_perfil.simpledialog,
        "askstring",
        lambda *a, **k: _CONTRASENA,
    )
    monkeypatch.setattr(
        vista_perfil.messagebox,
        "showinfo",
        lambda *a, **k: None,
    )

    VistaPerfil._solicitar_eliminacion(vista)

    assert completadas == [True]
    assert not contexto.sesion.hay_sesion_iniciada()


def prueba_cambio_contrasena_persiste_hash_y_conserva_datos(tmp_path):
    contexto = _crear_contexto(tmp_path)
    usuario_antes = contexto.sesion.usuario_actual()
    credenciales_usuario_antes = (
        usuario_antes.hash_contrasena,
        usuario_antes.sal,
    )
    credenciales_tercero = (
        contexto.autenticacion.obtener_por_id(1).hash_contrasena,
        contexto.autenticacion.obtener_por_id(1).sal,
    )
    amistades_antes = contexto.repositorio_amistades.cargar_todo()
    publicaciones_antes = contexto.repositorio_publicaciones.cargar_todo()

    contexto.autenticacion.cambiar_contrasena(
        _CONTRASENA,
        "nueva-clave-456",
        "nueva-clave-456",
    )

    usuario_guardado = next(
        usuario
        for usuario in contexto.repositorio_usuarios.cargar_todo()
        if usuario.id_usuario == usuario_antes.id_usuario
    )
    assert usuario_antes.id_usuario == usuario_guardado.id_usuario
    assert usuario_antes.nombre == usuario_guardado.nombre
    assert usuario_guardado.sal != credenciales_usuario_antes[1]
    assert usuario_guardado.hash_contrasena != credenciales_usuario_antes[0]
    assert contexto.sesion.usuario_actual() is usuario_antes
    assert contexto.sesion.hay_sesion_iniciada()
    assert (
        contexto.autenticacion.obtener_por_id(1).hash_contrasena,
        contexto.autenticacion.obtener_por_id(1).sal,
    ) == credenciales_tercero
    assert contexto.repositorio_amistades.cargar_todo() == amistades_antes
    assert contexto.repositorio_publicaciones.cargar_todo() == publicaciones_antes

    contexto.autenticacion.cerrar_sesion()
    with pytest.raises(ErrorAutenticacion):
        contexto.autenticacion.iniciar_sesion("persona2", _CONTRASENA)
    usuario_iniciado = contexto.autenticacion.iniciar_sesion(
        "persona2",
        "nueva-clave-456",
    )
    assert usuario_iniciado.id_usuario == usuario_antes.id_usuario


def prueba_cambio_contrasena_rechaza_clave_actual_incorrecta(tmp_path):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)
    credenciales_antes = (
        contexto.sesion.usuario_actual().hash_contrasena,
        contexto.sesion.usuario_actual().sal,
    )

    with pytest.raises(ErrorAutenticacion, match="incorrecta"):
        contexto.autenticacion.cambiar_contrasena(
            "clave-incorrecta",
            "otra-clave-456",
            "otra-clave-456",
        )

    assert _bytes_archivos(tmp_path) == archivos_antes
    assert (
        contexto.sesion.usuario_actual().hash_contrasena,
        contexto.sesion.usuario_actual().sal,
    ) == credenciales_antes


@pytest.mark.parametrize(
    ("actual", "nueva", "confirmacion"),
    (
        ("", "nueva-clave-456", "nueva-clave-456"),
        (_CONTRASENA, "", ""),
        (_CONTRASENA, "nueva-clave-456", ""),
    ),
)
def prueba_cambio_contrasena_rechaza_campos_vacios(
    tmp_path,
    actual,
    nueva,
    confirmacion,
):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)

    with pytest.raises(ErrorValidacion, match="obligatorios"):
        contexto.autenticacion.cambiar_contrasena(
            actual,
            nueva,
            confirmacion,
        )

    assert _bytes_archivos(tmp_path) == archivos_antes


def prueba_cambio_contrasena_rechaza_confirmacion_diferente(tmp_path):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)

    with pytest.raises(ErrorValidacion, match="no coinciden"):
        contexto.autenticacion.cambiar_contrasena(
            _CONTRASENA,
            "nueva-clave-456",
            "otra-clave-456",
        )

    assert _bytes_archivos(tmp_path) == archivos_antes


def prueba_cambio_contrasena_rechaza_reutilizar_la_actual(tmp_path):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)

    with pytest.raises(ErrorValidacion, match="diferente"):
        contexto.autenticacion.cambiar_contrasena(
            _CONTRASENA,
            _CONTRASENA,
            _CONTRASENA,
        )

    assert _bytes_archivos(tmp_path) == archivos_antes


def prueba_cambio_contrasena_aplica_minimo_de_seis_caracteres(tmp_path):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)

    with pytest.raises(ErrorValidacion, match="al menos 6 caracteres"):
        contexto.autenticacion.cambiar_contrasena(
            _CONTRASENA,
            "corta",
            "corta",
        )

    assert _bytes_archivos(tmp_path) == archivos_antes


def prueba_fallo_al_guardar_conserva_credenciales_en_archivo_y_memoria(
    tmp_path,
    monkeypatch,
):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)
    usuario = contexto.sesion.usuario_actual()
    credenciales_antes = (usuario.hash_contrasena, usuario.sal)

    def fallar_guardado(_usuarios):
        raise ErrorAlmacenamiento("No se pudo guardar el archivo de prueba.")

    monkeypatch.setattr(
        contexto.repositorio_usuarios,
        "guardar_todo",
        fallar_guardado,
    )

    with pytest.raises(ErrorAlmacenamiento, match="guardar"):
        contexto.autenticacion.cambiar_contrasena(
            _CONTRASENA,
            "nueva-clave-456",
            "nueva-clave-456",
        )

    assert _bytes_archivos(tmp_path) == archivos_antes
    assert (usuario.hash_contrasena, usuario.sal) == credenciales_antes
    assert contexto.sesion.hay_sesion_iniciada()


def prueba_cancelar_dialogo_cambio_contrasena_no_modifica_datos(tmp_path):
    contexto = _crear_contexto(tmp_path)
    archivos_antes = _bytes_archivos(tmp_path)
    dialogo = SimpleNamespace(destruido=False)
    dialogo.destroy = lambda: setattr(dialogo, "destruido", True)

    VistaPerfil._cancelar_dialogo_cambio_contrasena(dialogo)

    assert dialogo.destruido
    assert _bytes_archivos(tmp_path) == archivos_antes
    contexto.autenticacion.verificar_contrasena_actual(_CONTRASENA)


def prueba_cerrar_sesion_desde_perfil_regresa_al_login(monkeypatch, tmp_path):
    contexto = _crear_contexto(tmp_path)
    regresos_al_login = []
    destrucciones = []
    padre = SimpleNamespace(
        volver_al_login=lambda: regresos_al_login.append(True)
    )
    ventana = SimpleNamespace(
        _cerrando=False,
        _servicio_autenticacion=contexto.autenticacion,
        master=padre,
        destroy=lambda: destrucciones.append(True),
    )
    monkeypatch.setattr(
        ventana_principal.messagebox,
        "askyesno",
        lambda *args, **kwargs: True,
    )

    ventana_principal.VentanaPrincipal._cerrar_sesion(ventana)

    assert not contexto.sesion.hay_sesion_iniciada()
    assert destrucciones == [True]
    assert regresos_al_login == [True]
