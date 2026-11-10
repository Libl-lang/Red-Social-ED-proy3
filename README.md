# Social UNA — Red Social Universitaria

Proyecto final de Estructuras de Datos. Aplicación de escritorio (Tkinter) que permite a usuarios registrarse, iniciar sesión, buscar amigos, agregar contactos y publicar mensajes en un muro, todo persistido en archivos JSON.

---

## 📋 Índice

- [Descripción general](#descripción-general)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Fase 2 — Integración: cambios y adiciones](#fase-2--integración-cambios-y-adiciones)
- [Módulos de la aplicación](#módulos-de-la-aplicación)
- [Reglas de persistencia y datos](#reglas-de-persistencia-y-datos)
- [IDs como enteros en el grafo de amistades](#ids-como-enteros-en-el-grafo-de-amistades)
- [Refresco de vistas al cambiar de pestaña](#refresco-de-vistas-al-cambiar-de-pestaña)
- [Contratos entre módulos](#contratos-entre-módulos)
- [Cómo ejecutar la aplicación](#cómo-ejecutar-la-aplicación)
- [Cómo ejecutar las pruebas](#cómo-ejecutar-las-pruebas)
- [Piezas falsas (mocks) para pruebas unitarias](#piezas-falsas-mocks-para-pruebas-unitarias)

## Descripción general

**Social UNA** es una red social universitaria desarrollada en Python dividida en tres módulos:

| Módulo | Responsabilidad | Archivo clave |
|--------|-----------------|---------------|
| **M1 — Autenticación** | Registro, inicio de sesión, cierre de sesión y directorio de usuarios | `servicio_autenticacion.py`, `sesion.py` |
| **M2 — Social** | Búsqueda de usuarios, grafo de amistades, agregar amigos | `servicio_social.py`, `grafo_amistades.py` |
| **M3 — Publicaciones** | Crear publicaciones, armar el muro (propias + de amigos) | `servicio_publicaciones.py`, `historial_publicaciones.py` |

Los módulos se comunican a través de **contratos del dominio** (`src/social_una/dominio/contratos.py`) que definen las interfaces que cada pieza debe cumplir, permitiendo inyección de dependencias y pruebas aisladas con piezas falsas.

## Estructura del proyecto

```
Red-Social-ED-proy3/
├── README.md
├── pytest.ini                 # Configuración de pytest
├── requirements-dev.txt       # Dependencias de desarrollo (pytest)
├── datos/
│   └── semilla/
│       └── amistades.json     # Datos de semilla (amistades iniciales)
├── desarrollo/
│   ├── lanzar_autenticacion.py
│   ├── lanzar_muro.py
│   └── lanzar_social.py       # Lanzadores individuales por módulo (desarrollo)
├── src/
│   └── social_una/
│       ├── __init__.py
│       ├── principal.py       # Punto de entrada de la aplicación
│       ├── composicion.py     # ⭐ Integración: construye y conecta todos los componentes
│       ├── dominio/
│       │   ├── contratos.py   # Interfaces (DirectorioUsuarios, SesionActiva, ConsultaAmistades, Repositorios)
│       │   ├── errores.py     # Excepciones de negocio
│       │   └── modelos.py     # Usuario, Publicacion
│       ├── almacenamiento/
│       │   ├── almacen_json.py                 # Lectura/escritura segura de JSON
│       │   ├── repositorio_usuarios_json.py
│       │   ├── repositorio_amistades_json.py
│       │   └── repositorio_publicaciones_json.py
│       ├── estructuras/
│       │   ├── catalogo_usuarios.py
│       │   ├── grafo_amistades.py
│       │   └── historial_publicaciones.py
│       ├── servicios/
│       │   ├── sesion.py
│       │   ├── servicio_autenticacion.py
│       │   ├── servicio_social.py
│       │   └── servicio_publicaciones.py
│       └── interfaz/
│           ├── alertas.py
│           ├── ventana_principal.py
│           ├── vista_autenticacion.py
│           ├── vista_social.py
│           └── vista_muro.py
└── pruebas/
    ├── falsos/                      # 🛡️ Piezas falsas para pruebas unitarias (NO modificar)
    │   ├── directorio_usuarios_falso.py
    │   ├── consulta_amistades_falsa.py
    │   ├── sesion_falsa.py
    │   └── repositorios_en_memoria.py
    └── unitarias/
        ├── m2_social/
        │   ├── prueba_grafo.py
        │   ├── prueba_repositorio.py
        │   └── prueba_servicio.py
        └── m3_publicaciones/
            ├── prueba_historial_publicaciones.py
            ├── prueba_repositorio_publicaciones_json.py
            └── prueba_servicio_publicaciones.py

## Fase 2 — Integración: cambios y adiciones

Esta fase conecta los tres módulos (M1 + M2 + M3) en una sola aplicación funcionando de extremo a extremo. A continuación se detallan los cambios y adiciones realizados.

### `src/social_una/composicion.py` (archivo principal modificado)

Se reescribió completamente para pasar de un esqueleto parcial (`crear_servicios()` que solo conectaba M1) a una composición completa de todos los componentes. La función `construir_aplicacion(ruta_datos)` sigue ahora el **orden estricto de inyección de dependencias**:

1. **Persistencia inicial** — `_configurar_persistencia_inicial(ruta_datos, ruta_semilla)` crea la carpeta de ejecución y copia los archivos de semilla (p. ej. `amistades.json`) desde `datos/semilla/` solo si aún no existen en ejecución. Nunca sobrescribe archivos ya creados por la aplicación, por lo que los datos del usuario se conservan entre reinicios.
2. **Almacenamiento y repositorios reales** — Se instancia `AlmacenJson` y los tres repositorios reales:
   - `RepositorioUsuariosJson(almacen, ruta_datos / "usuarios.json")`
   - `RepositorioAmistadesJson(ruta_datos / "amistades.json")`
   - `RepositorioPublicacionesJson(ruta_datos / "publicaciones.json", almacen)`
3. **Sesión y ServicioAutenticacion** — Se crea `Sesion()` y `ServicioAutenticacion(repositorio_usuarios, sesion)`, el cual cumple el contrato `DirectorioUsuarios`.
4. **ServicioSocial** — Se crea inyectándole el repositorio de amistades, el servicio de autenticación y la sesión. Cumple el contrato `ConsultaAmistades`.
5. **ServicioPublicaciones** — Se crea inyectándole el repositorio de publicaciones, el servicio social, el servicio de autenticación y la sesión.
6. **VentanaPrincipal** — Se instancia pasándole los tres servicios reales y la sesión.

La función devuelve un diccionario con todos los componentes construidos para facilitar su uso desde `principal.py`.

### `src/social_una/principal.py`

Se actualizó el punto de entrada para usar `construir_aplicacion("datos")` en lugar del antiguo `crear_servicios()`. Ahora obtiene los tres servicios (`autenticacion`, `social`, `publicaciones`) y la `sesion` del diccionario retornado, y los pasa a `VentanaPrincipal` tras el inicio de sesión exitoso.

### `src/social_una/interfaz/ventana_principal.py`

Se adaptó `VentanaPrincipal` para recibir los tres servicios reales y la sesión en lugar de parámetros sueltos de M1. Mantiene la navegación entre pestañas (publicaciones / amistades) con refresco automático de las vistas.

### `src/social_una/interfaz/vista_social.py`

Se refactorizó para almacenar las referencias de los widgets (`_lista_amigos`, `_frame_amigos`, `_etiqueta_estado`) como atributos de instancia, permitiendo que `VentanaPrincipal` invoque `_refrescar_amigos()` al cambiar a la pestaña de amistades.

## Módulos de la aplicación

### M1 — Autenticación (`servicio_autenticacion.py`, `sesion.py`)

- `ServicioAutenticacion` implementa `DirectorioUsuarios`: `obtener_por_id(id)`, `buscar(texto)`, `existe(id)`.
- Maneja registro con hash de contraseña (PBKDF2-SHA256 con sal aleatoria), inicio de sesión, cierre de sesión y catálogo de usuarios en memoria (`CatalogoUsuarios`).
- `Sesion` implementa `SesionActiva`: `usuario_actual()`, `hay_sesion_iniciada()`, `iniciar(usuario)`, `cerrar()`.

### M2 — Social (`servicio_social.py`, `grafo_amistades.py`)

- `ServicioSocial` implementa `ConsultaAmistades`: `obtener_ids_amigos(id)`, `son_amigos(id_a, id_b)`.
- Operaciones propias: `buscar_usuarios(texto)`, `agregar_amigo(id_amigo)`, `listar_mis_amigos()`.
- `GrafoAmistades` es un grafo no dirigido con lista de adyacencia; cada amistad se guarda en ambos sentidos y se exporta una sola vez con `id_a < id_b`.

### M3 — Publicaciones (`servicio_publicaciones.py`, `historial_publicaciones.py`)

- `ServicioPublicaciones`: `publicar(texto)`, `obtener_muro()`, `obtener_muro_personal()`, `obtener_nombre_autor(id_autor)`.
- El muro incluye publicaciones propias y de amigos, ordenadas de la más reciente a la más antigua.
- `HistorialPublicaciones` mantiene el orden de inserción y calcula el siguiente ID disponible.

## Reglas de persistencia y datos

- **Almacenamiento seguro**: `AlmacenJson.escribir_seguro()` escribe primero en un archivo temporal (`.tmp`) en la misma carpeta y, solo al terminar sin errores, lo reemplaza sobre el original con `os.replace()`. Si falla, el archivo original queda intacto y no queda basura temporal.
- **Semilla de ejecución**: al iniciar la app, `construir_aplicacion` copia `datos/semilla/amistades.json` a la carpeta de ejecución si aún no existe ahí. Los archivos generados por el usuario (usuarios, publicaciones, amistades nuevas) nunca se sobrescriben.
- **Archivos de datos generados en ejecución**: `usuarios.json`, `amistades.json`, `publicaciones.json` dentro de la carpeta indicada por `ruta_datos` (por defecto `"datos"`).
- **Codificación**: todos los archivos JSON se leen/escriben con UTF-8, conservando tildes, eñes y caracteres especiales.

## IDs como enteros en el grafo de amistades

Una regla crítica del proyecto es que **todos los IDs de usuarios se manejan como enteros** para evitar problemas de llaves de texto al cargar desde JSON:

- `GrafoAmistades` convierte a `int` en `agregar_amistad`, `obtener_amigos`, `son_amigos`, `cargar_pares` y `exportar_pares`.
- `RepositorioAmistadesJson.cargar_todo()` convierte cada par a `(int, int)` antes de devolverlo.
- `RepositorioAmistadesJson.guardar_todo()` guarda los pares como `[[int, int]]`.
- `Usuario.desde_diccionario()` y `Publicacion.desde_diccionario()` convierten `id_usuario`, `id_publicacion` e `id_autor` a `int`.

Esto garantiza que las amistades cargadas desde JSON (donde podrían venir como strings) funcionen correctamente con el grafo.

## Refresco de vistas al cambiar de pestaña

`VentanaPrincipal` coordina la navegación entre dos vistas y refresca cada una al mostrarse:

- **Pestaña Publicaciones** (`_mostrar_publicaciones`): crea `VistaMuro` y llama a `vista_muro.refrescar()` para redibujar las tarjetas del muro con los datos más recientes del servicio.
- **Pestaña Amistades** (`_mostrar_amistades`): crea `VistaSocial` y llama a `vista_social._refrescar_amigos()` para actualizar la lista de amigos del usuario activo.

Además, las vistas se refrescan automáticamente tras acciones del usuario:
- Tras publicar un mensaje (`VistaMuro._al_publicar` → `self.refrescar()`).
- Tras agregar un amigo (`VistaSocial._agregar_amigo_seleccionado` → `self._refrescar_amigos()`).

## Contratos entre módulos

Definidos en `src/social_una/dominio/contratos.py`:

| Contrato | Métodos | Implementa | Usado por |
|----------|---------|------------|-----------|
| `DirectorioUsuarios` | `obtener_por_id(id)`, `buscar(texto)`, `existe(id)` | `ServicioAutenticacion` (M1) | M2, M3 |
| `SesionActiva` | `usuario_actual()`, `hay_sesion_iniciada()` | `Sesion` (M1) | M2, M3 |
| `ConsultaAmistades` | `obtener_ids_amigos(id)`, `son_amigos(a, b)` | `ServicioSocial` (M2) | M3 |
| `RepositorioUsuarios` | `cargar_todo()`, `guardar_todo(usuarios)` | `RepositorioUsuariosJson` | `ServicioAutenticacion` |
| `RepositorioAmistades` | `cargar_todo()`, `guardar_todo(pares)` | `RepositorioAmistadesJson` | `ServicioSocial` |
| `RepositorioPublicaciones` | `cargar_todo()`, `guardar_todo(pubs)` | `RepositorioPublicacionesJson` | `ServicioPublicaciones` |

## Cómo ejecutar la aplicación

Desde la raíz del proyecto (`Red-Social-ED-proy3`):

```bash
# Opción 1: ejecutar el módulo principal directamente
python -m src.social_una.principal

# Opción 2: desde la carpeta src
cd src
python -m social_una.principal
```

La aplicación abre primero la ventana de **Acceso** (inicio de sesión / registro). Tras autenticarse, se abre la **Ventana Principal** con dos pestañas: **Publicaciones** y **Amistades**.

## Cómo ejecutar las pruebas

Desde la raíz del proyecto:

```bash
python -m pytest pruebas -v
```

Resultado esperado: **77 passed** (29 pruebas de M2 social + 48 pruebas de M3 publicaciones). Todas las pruebas usan las piezas falsas de `pruebas/falsos/` y `tmp_path` de pytest, por lo que no tocan los datos reales del proyecto.

Dependencia requerida: `pytest>=8.0` (listada en `requirements-dev.txt`).

## Piezas falsas (mocks) para pruebas unitarias

El directorio `pruebas/falsos/` contiene implementaciones simuladas que cumplen los contratos del dominio y se usan exclusivamente en las pruebas unitarias con pytest:

- `DirectorioUsuariosFalso` — usuarios fijos (Ana, Beto, Carla) con datos predefinidos.
- `ConsultaAmistadesFalsa` — amistades simuladas mediante diccionario `id -> set de ids`.
- `SesionFalsa` — sesión con un usuario fijo configurable.
- `RepositorioUsuariosEnMemoria`, `RepositorioAmistadesEnMemoria`, `RepositorioPublicacionesEnMemoria` — repositorios que guardan en listas en memoria.

> ⚠️ **Estas clases no deben modificarse ni eliminarse**, ya que son necesarias para las pruebas unitarias aisladas de cada módulo.

## Notas finales

- El proyecto está en la rama `develop` y está sincronizado con `origin/develop`.
- Python requerido: 3.10+ (usa `str | Path` y `list[T]`/`set[T]` tipados).
- Interfaz gráfica basada en Tkinter (estándar de Python, sin dependencias externas).