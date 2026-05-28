# Estructura del proyecto `software_inventario_laboratorios`

Documento generado el 2026-04-30 a partir de la estructura local del proyecto.
Actualizado el 2026-05-27 con el modulo de Protocolos.

## Resumen general

Este proyecto es una aplicacion web en Flask para gestionar inventario de laboratorios. La aplicacion usa MySQL/MariaDB mediante `Flask-MySQLdb`, autenticacion con `Flask-Login`, proteccion CSRF con `Flask-WTF`, plantillas Jinja2 y archivos estaticos para estilos, imagenes, documentos PDF y scripts de interfaz.

La mayor parte de la logica funcional esta concentrada en `routes.py`. El archivo `app.py` inicializa la aplicacion Flask, registra el blueprint `inventario` y monta la aplicacion bajo el prefijo `/inventario-laboratorios`.

## Arbol de archivos

> Nota: se excluyen los contenidos internos de `.git` y los archivos `__pycache__`, porque son metadatos/generados y no forman parte de la estructura funcional del sistema. Si existen localmente, no deberian editarse manualmente.

```text
software_inventario_laboratorios/
|-- .gitignore
|-- README.md
|-- app.py
|-- app.wsgi
|-- config.py
|-- email_devolucion.py
|-- email_service.py
|-- extensions.py
|-- requirements.txt
|-- routes.py
|-- database/
|   `-- flask_login.sql
|-- models/
|   |-- __init__.py
|   |-- ModelUser.py
|   `-- entities/
|       `-- User.py
|-- static/
|   |-- css/
|   |   |-- DSC_0183.JPG
|   |   |-- Fondo_Colmayor.jpg
|   |   |-- estilos.css
|   |   |-- indexSalud.css
|   |   |-- inv_3.jpg
|   |   |-- layout.css
|   |   `-- login.css
|   |-- fotos/
|   |   |-- 08-03-2025.PNG
|   |   |-- 1laboratorio.jpg
|   |   |-- 1tdea.png
|   |   |-- 2tdea.png
|   |   |-- ACTIVIDAD_PAULI.pdf
|   |   |-- banderaMexico.jpg
|   |   |-- barbie.jpg
|   |   |-- biorreactor.PNG
|   |   |-- Candy.jpg
|   |   |-- equipo_dell.jpeg
|   |   |-- hal.png
|   |   |-- indisponibilidad_sigep.PNG
|   |   |-- inv_3.jpg
|   |   |-- lav.PNG
|   |   |-- logosex-3.png
|   |   |-- microscopio.jpeg
|   |   |-- multi1.jpeg
|   |   |-- RECETAS.pdf
|   |   |-- satis1.webp
|   |   |-- siluetaP.png
|   |   `-- TdeA-1.png
|   |-- img/
|   |   |-- Escudo_Colmayor.png
|   |   |-- flask.svg
|   |   |-- INFORME_TECNICO_BAJAS.xlsx
|   |   |-- Logo-Colmayor-Color-Blanco-1.png
|   |   |-- logo-correo.gif
|   |   |-- logo.png
|   |   `-- siluetapp.png
|   |-- js/
|   |   `-- inventario.js
|   `-- pdf/
|       |-- ACTIVIDAD_PAULI.pdf
|       |-- Anexo_1_Solicitud_de_costos_o_deducciones.pdf
|       |-- BANO_MARIA.pdf
|       `-- CERTIFICADO_ALTURAS.pdf
`-- templates/
    |-- agregarNuevoProveedor.html
    |-- base.html
    |-- datosProveedorSalud.html
    |-- edit-producto.html
    |-- editar_producto_indexSalud.html
    |-- equiposDeBajaSalud.html
    |-- historialFechas.html
    |-- historialPrestamoSalud.html
    |-- home.html
    |-- indexSalud.html
    |-- layout.html
    |-- prestamos_equipos_salud.html
    |-- protocolo_equipo.html
    |-- protocolos_generales.html
    `-- auth/
        `-- login.html
```

## Archivos principales de la raiz

| Archivo | Proposito |
| --- | --- |
| `app.py` | Punto de entrada de Flask. Crea `app`, carga configuracion de desarrollo, registra el blueprint `inventario`, inicializa `csrf`, `db` y `login_manager`, y define manejadores 401/404. |
| `routes.py` | Modulo central de rutas y logica de negocio: login, home, inventario por modulo, proveedores, productos/equipos, carga de imagen/PDF/CSV, exportaciones, mantenimientos, calibraciones, prestamos, devoluciones, equipos dados de baja y protocolos. |
| `config.py` | Configuracion de entornos, conexion MySQL, correo SMTP y enlaces OneDrive. Contiene datos sensibles y conviene migrarlos a variables de entorno. |
| `extensions.py` | Instancia extensiones compartidas: `CSRFProtect`, `MySQL` y `LoginManager`. |
| `email_service.py` | Construye y envia correos HTML para notificaciones de prestamo, incluyendo logo institucional embebido. |
| `email_devolucion.py` | Construye y envia correos HTML para notificaciones de devolucion de equipos. |
| `app.wsgi` | Archivo de despliegue WSGI para servidor Linux/Apache, insertando `/var/www/software_inventario_laboratorios` en `sys.path`. |
| `requirements.txt` | Dependencias Python del proyecto. Incluye Flask, Flask-Login, Flask-MySQLdb, Flask-WTF, openpyxl, pandas, selenium, xhtml2pdf, entre otras. |
| `README.md` | README actual muy basico, solo contiene el nombre del proyecto. |
| `.gitignore` | Reglas para ignorar archivos en Git. |

## Estructura de aplicacion Flask

```text
app.py
`-- registra routes.bp como blueprint "inventario"
    `-- url_prefix="/inventario-laboratorios"
        `-- routes.py define las vistas y endpoints
```

Componentes relevantes:

- Blueprint principal: `bp = Blueprint('inventario', __name__)`.
- URL base del sistema: `/inventario-laboratorios`.
- Ruta estatica configurada en `app.py`: `/inventario-laboratorios/static`.
- Login manager: `login_manager.login_view = "inventario.login"`.
- Usuario cargado desde BD con `ModelUser.get_by_id(db, id)`.
- La respuesta del blueprint desactiva cache con `@bp.after_request`.

## Rutas principales

| Ruta | Funcion | Metodo | Proposito |
| --- | --- | --- | --- |
| `/` | `index` | GET | Redirige al login. |
| `/login` | `login` | GET/POST | Autentica usuarios y redirige segun rol. |
| `/logout` | `logout` | GET | Cierra sesion. |
| `/home` | `home` | GET | Panel con resumen de vencimientos de mantenimiento y calibracion. |
| `/datosProveedorSalud/<id>` | `datosProveedorSalud` | GET | Consulta datos de proveedor. |
| `/update_datos_proveedor_salud/<id>` | `ACTUALIZAR_DATOS_PROVEEDOR_SALUD` | POST | Actualiza proveedor. |
| `/agregarNuevoProveedor` | `agregarNuevoProveedor` | GET | Muestra formulario para proveedor nuevo. |
| `/add_datos_proveedor_salud` | `AGREGAR_DATOS_PROVEEDOR_SALUD` | POST | Inserta proveedor nuevo. |
| `/<modulo>` | `index_modulo` | GET | Lista equipos activos por modulo: salud, gastronomia, lacma o arquitectura. |
| `/<modulo>/add_productoSalud` | `AGREGAR_PRODUCTO_SALUD` | GET/POST | Crea un equipo y guarda imagen/PDF si aplica. |
| `/subir_imagen/<int:id_producto>` | `subir_imagen` | POST | Actualiza imagen de un equipo. |
| `/subir_pdf/<int:id_producto>` | `subir_pdf` | GET/POST | Actualiza guia PDF de un equipo. |
| `/<modulo>/insert_csv` | `insert_csv` | POST | Importa equipos desde CSV. |
| `/updateDate_csv` | `updateDate_csv` | POST | Actualiza fechas masivamente desde CSV. |
| `/exportCsvsalud` | `exportCsv` | GET | Exporta equipos activos a CSV. |
| `/exportExcelSaludDeBaja` | `exportExcelDeBaja` | POST | Exporta equipos dados de baja usando plantilla Excel. |
| `/checkbox_programacionMantenimiento` | `checkbox_programacionMantenimiento` | POST | Actualiza estado de programacion de mantenimiento/calibracion. |
| `/guardar_historial_masivo` | `guardar_historial_masivo` | POST | Guarda historial masivo de mantenimiento/calibracion. |
| `/<modulo>/update_estado_equipo` | `update_estado_equipo` | POST | Cambia estado del equipo; maneja prestamos, devoluciones y baja. |
| `/prestamos_equipos_salud/<cod_articulo>` | `prestamos_equipos_salud` | GET | Muestra datos del prestamo activo de un equipo. |
| `/historialPrestamoSalud` | `historial_prestamo_salud` | GET | Lista historial de prestamos. |
| `/edit_productoSalud/<id>/<vista>` | `GET_PRODUCTO_SALUD` | GET | Muestra hoja de vida/edicion de equipo. |
| `/actualizarSalud/<id>` | `ACTUALIZAR_PRODUCTO_SALUD` | POST | Actualiza datos de equipo. |
| `/historialFechas/<cod_articulo>` | `historialFechas` | GET | Muestra historial de mantenimiento y calibracion. |
| `/update_historial_fechas` | `update_historial_fechas` | POST | Actualiza ultimo registro de historial de mantenimiento. |
| `/update_historial_fechas_calibracion` | `update_historial_fechas_calibracion` | POST | Actualiza ultimo registro de historial de calibracion. |
| `/equiposDeBajaSalud` | `equiposDeBajaSalud` | GET | Lista equipos dados de baja. |
| `/delete_productoSalud/<string:id>` | `ELIMINAR_CONTACTO_SALUD` | GET | Desactiva equipo con `enable=0`. |
| `/<modulo>/protocolos/equipo/<int:equipo_id>` | `protocolo_equipo` | GET | Muestra los protocolos activos asociados a un equipo especifico del modulo. |
| `/<modulo>/protocolos` | `protocolos_generales` | GET | Lista todos los protocolos activos registrados para un modulo. |
| `/<modulo>/protocolos/equipo/<int:equipo_id>/agregar` | `agregar_protocolo` | POST | Inserta un protocolo nuevo desde el modal de la vista especifica del equipo. |

## Modelos

```text
models/
|-- ModelUser.py
`-- entities/
    `-- User.py
```

### `models/entities/User.py`

Define la entidad `User`, que hereda de `UserMixin` para integrarse con `Flask-Login`.

Campos manejados:

- `id`
- `username`
- `password`
- `fullname`
- `rol`

Tambien incluye `check_password`, que valida contrasenas hasheadas con `werkzeug.security.check_password_hash`.

### `models/ModelUser.py`

Contiene consultas relacionadas con usuarios:

- `login(db, user)`: busca el usuario por `username`, valida contrasena y devuelve una instancia de `User`.
- `get_by_id(db, id)`: busca usuario por id para reconstruir la sesion de Flask-Login.

## Base de datos

El archivo disponible en `database/flask_login.sql` contiene un dump antiguo/base para la tabla `user`.

Tablas detectadas por consultas en el codigo:

| Tabla | Uso en el sistema |
| --- | --- |
| `user` | Usuarios, autenticacion, roles y datos del usuario logueado. |
| `indexssalud` | Tabla principal de equipos activos/inventario por modulo. |
| `datosproveedorsalud` | Proveedores responsables y contactos. |
| `estados_equipos` | Catalogo de estados posibles de equipos. |
| `ubicacion_equipos` | Catalogo de ubicaciones originales. |
| `equipossalud_debaja` | Equipos marcados como dados de baja. |
| `prestamos_equiposalud` | Prestamos activos e historicos de equipos. |
| `historial_mantenimiento_salud` | Historial de mantenimientos. |
| `historial_calibracion_salud` | Historial de calibraciones. |
| `protocolos` | Protocolos de mantenimiento preventivo asociados a equipos de `indexssalud`. |

El dump `flask_login.sql` no refleja todas las tablas usadas actualmente por `routes.py`; para reconstruir todo el sistema se necesitara un dump mas completo de la base de datos `flaskinventario`.

### Tabla `protocolos`

La tabla `protocolos` se consulta desde el modulo nuevo de Protocolos. Segun las rutas actuales, los campos esperados son:

- `id`
- `equipo_id`
- `anio`
- `actividades_de_mantenimiento_preventivo`
- `proveedor_interno`
- `proveedor_externo`
- `enable`
- `de_baja`
- `fecha_baja`

`equipo_id` se usa para relacionar cada protocolo con `indexssalud.id`. Los datos de codigo, nombre y modulo del equipo no se duplican en la vista, sino que se obtienen mediante `INNER JOIN` con `indexssalud`.

## Plantillas

```text
templates/
|-- base.html
|-- layout.html
|-- home.html
|-- indexSalud.html
|-- agregarNuevoProveedor.html
|-- datosProveedorSalud.html
|-- editar_producto_indexSalud.html
|-- edit-producto.html
|-- equiposDeBajaSalud.html
|-- historialFechas.html
|-- historialPrestamoSalud.html
|-- prestamos_equipos_salud.html
|-- protocolo_equipo.html
|-- protocolos_generales.html
`-- auth/
    `-- login.html
```

| Plantilla | Proposito |
| --- | --- |
| `base.html` | Base para la pantalla de login. Define titulo, favicon, Bootstrap y bloques Jinja. |
| `auth/login.html` | Formulario de inicio de sesion. |
| `layout.html` | Layout principal autenticado: menu lateral, navegacion por modulos, enlaces de exportacion, proveedores, baja, historial, protocolos generales y logout. |
| `home.html` | Vista resumen del sistema con indicadores de vencimiento. |
| `indexSalud.html` | Vista principal del inventario por modulo; incluye formularios de alta, importacion, tabla, acciones, prestamos y boton individual de protocolo por equipo. |
| `agregarNuevoProveedor.html` | Formulario para crear proveedores. |
| `datosProveedorSalud.html` | Visualizacion/edicion de datos del proveedor. |
| `editar_producto_indexSalud.html` | Hoja de vida y edicion de equipo. |
| `edit-producto.html` | Plantilla antigua o no conectada al blueprint actual; conserva referencias a rutas sin prefijo `inventario`. |
| `equiposDeBajaSalud.html` | Lista equipos dados de baja. |
| `historialFechas.html` | Historial de mantenimiento y calibracion. |
| `historialPrestamoSalud.html` | Historial de prestamos. |
| `prestamos_equipos_salud.html` | Detalle de prestamo activo. |
| `protocolo_equipo.html` | Vista especifica de protocolos activos de un equipo, accesible desde el boton `Protocolo` en la columna `Acciones`; incluye modal para registrar protocolos nuevos. |
| `protocolos_generales.html` | Vista centralizada que lista protocolos activos de todos los equipos del modulo actual. |

## Archivos estaticos

```text
static/
|-- css/
|-- fotos/
|-- img/
|-- js/
`-- pdf/
```

### `static/css`

Contiene hojas de estilo y algunas imagenes usadas como fondos o recursos visuales:

- `estilos.css`
- `layout.css`
- `login.css`
- `indexSalud.css`
- `Fondo_Colmayor.jpg`
- `DSC_0183.JPG`
- `inv_3.jpg`

### `static/js`

- `inventario.js`: maneja interacciones del inventario, especialmente seleccion masiva de mantenimientos/calibraciones, envio de datos por `fetch`, validaciones de campos y desactivacion automatica segun vencimientos.

### `static/img`

Recursos institucionales y plantillas:

- Logos e imagenes del Colegio Mayor.
- `logo-correo.gif`, usado en correos.
- `INFORME_TECNICO_BAJAS.xlsx`, plantilla para exportar equipos dados de baja.

### `static/fotos`

Carpeta de imagenes y documentos cargados/asociados a equipos. Contiene archivos de prueba o datos reales, por ejemplo fotos de equipos y algunos PDF.

### `static/pdf`

Carpeta de guias o documentos PDF asociados a equipos.

## Servicios de correo

Hay dos modulos separados:

- `email_service.py`: notificaciones de prestamo.
- `email_devolucion.py`: notificaciones de devolucion.

Ambos construyen mensajes HTML con firma institucional y adjuntan `static/img/logo-correo.gif` como imagen embebida. Usan la configuracion SMTP definida en `config.py`.

## Importacion, exportacion y archivos

Funciones relevantes:

- Importacion CSV: `insert_csv`.
- Actualizacion masiva desde CSV: `updateDate_csv`.
- Exportacion CSV de equipos activos: `exportCsv`.
- Exportacion Excel de equipos dados de baja: `exportExcelDeBaja`.
- Carga de imagen de equipo: `AGREGAR_PRODUCTO_SALUD` y `subir_imagen`.
- Carga de PDF: `AGREGAR_PRODUCTO_SALUD` y `subir_pdf`.

Rutas de archivos usadas por el codigo:

- Imagenes en base de datos: `fotos/<archivo>`.
- PDF en base de datos: `pdf/<archivo>`.
- Carpeta PDF absoluta para despliegue: `/var/www/software_inventario_laboratorios/static/pdf`.

## Modulo de Protocolos

El modulo de Protocolos agrega dos formas de acceso:

- Acceso individual por equipo: en `templates/indexSalud.html`, la columna `Acciones` incluye el boton `Protocolo`, que apunta a `inventario.protocolo_equipo` usando el `id` del equipo y el `modulo`.
- Acceso general por modulo: en `templates/layout.html`, el menu lateral agrega `Protocolos Generales` cuando la ruta actual contiene un modulo valido. Este enlace apunta a `inventario.protocolos_generales`.

Rutas implementadas en `routes.py`:

- `/<modulo>/protocolos/equipo/<int:equipo_id>`: valida el modulo, consulta el equipo activo en `indexssalud` y luego lista sus protocolos activos en `protocolos`.
- `/<modulo>/protocolos`: valida el modulo y lista todos los protocolos activos de los equipos activos de ese modulo.
- `/<modulo>/protocolos/equipo/<int:equipo_id>/agregar`: recibe el formulario del modal, valida campos obligatorios e inserta el protocolo asociado al equipo.

Plantillas del modulo:

- `templates/protocolo_equipo.html`: muestra la informacion del equipo y sus protocolos asociados. Cuando no hay protocolos activos, ofrece el boton `Agregar Protocolo` y abre el modal `modalNuevoProtocolo`.
- `templates/protocolos_generales.html`: muestra una tabla general con codigo, nombre del equipo, anio, actividad de mantenimiento preventivo, proveedor interno, proveedor externo y accion para ver el protocolo especifico.

Formulario de creacion de protocolos:

- El modal de `protocolo_equipo.html` envia por POST a `inventario.agregar_protocolo`.
- Campos enviados: `anio`, `proveedor_interno`, `proveedor_externo` y `actividades`.
- `agregar_protocolo` guarda `actividades` en la columna `actividades_de_mantenimiento_preventivo`.
- La insercion crea registros con `enable = 1` y `de_baja = 0`, manteniendo la relacion con el equipo mediante `equipo_id`.
- Al guardar correctamente, la funcion redirige de nuevo a `protocolo_equipo` para mostrar el protocolo recien creado.

Integridad y sincronizacion:

- Los protocolos se relacionan con equipos mediante `protocolos.equipo_id = indexssalud.id`.
- La consulta general usa `INNER JOIN indexssalud i ON i.id = p.equipo_id`, evitando duplicar datos como codigo y nombre del equipo.
- Las vistas solo muestran protocolos con `p.enable = 1`, `p.de_baja = 0`, equipos con `i.enable = 1` e `i.de_baja = 0`.
- En `update_estado_equipo`, cuando un equipo pasa a `DE BAJA`, se actualizan sus protocolos con `enable = 0`, `de_baja = 1` y `fecha_baja = NOW()`.

## Roles y modulos

Roles detectados en login:

- `salud`
- `gastronomia`
- `lacma`
- `arquitectura`
- `tecnologia`
- `admin`

Modulos validos en `index_modulo`:

- `salud`
- `gastronomia`
- `lacma`
- `arquitectura`

Nota: el rol `tecnologia` aparece permitido en el login, pero no aparece dentro de `modulos_validos` de `index_modulo`; por lo tanto, un usuario con ese rol podria ser redirigido a un modulo que luego vuelve al `home`.

## Dependencias principales

Del archivo `requirements.txt`, las dependencias mas relacionadas con la aplicacion son:

- `Flask`
- `Flask-Login`
- `Flask-MySQLdb`
- `Flask-WTF`
- `Werkzeug`
- `Jinja2`
- `openpyxl`
- `pandas`
- `python-dateutil`
- `xhtml2pdf`
- `reportlab`
- `pillow`

Tambien hay dependencias para Google APIs, Selenium, PyInstaller y manejo de PDF/Excel que pueden ser necesarias para tareas auxiliares o historicas del proyecto.

## Observaciones tecnicas

- El proyecto esta organizado como una app Flask tradicional, pero `routes.py` concentra demasiada responsabilidad. A futuro convendria separar por dominios: autenticacion, equipos, proveedores, prestamos, exportaciones y mantenimiento/calibracion.
- `config.py` contiene credenciales y secretos escritos directamente en codigo. Es recomendable moverlos a variables de entorno o a un archivo `.env` no versionado.
- Varias rutas usan nombres historicos con `Salud`, aunque el sistema ya maneja varios modulos.
- Algunas plantillas y redirecciones conservan referencias sin namespace `inventario`, por ejemplo `url_for('index_modulo')`, lo que puede causar errores cuando todo esta dentro del blueprint.
- El dump SQL incluido solo define `user`, pero el codigo depende de mas tablas. Para documentar o desplegar el sistema completo hace falta un dump actualizado de `flaskinventario`.
- El modulo de Protocolos depende de que exista la tabla `protocolos` en la base de datos y de que `equipo_id` corresponda con `indexssalud.id`.
- Para completar la trazabilidad del modulo de Protocolos, conviene incluir la definicion SQL de `protocolos` en un dump actualizado o en un archivo de migracion.
