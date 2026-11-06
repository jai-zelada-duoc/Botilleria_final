# Registro de versiones

## v1.8.1 — Correcciones de arranque y validación CSV
- Se agregó `main.py` para iniciar el proyecto con `python main.py` desde la carpeta raíz.
- Si falta Tkinter, el arranque ahora explica cómo instalarlo en vez de mostrar un traceback críptico.
- La carga de CSV ahora informa IDs duplicados, nombres de producto duplicados y filas con columnas sobrantes.
- Se agregaron pruebas de regresión ejecutables con `python -m unittest discover -s tests -v`.
- Se corrigió la descripción del paquete, que todavía indicaba persistencia JSON.

## v1.8 — Nuevo Inicio, alta de productos y título centrado
- Inicio: productos, clientes y pedidos se muestran como cifras grandes (con unidades en stock, clientes VIP y pedidos por estado), y los módulos son fichas negras con texto verde claro y una flecha. Toda la ficha es clicable.
- Productos ahora tiene dos pestañas: **Productos en bodega** (tabla y botón de edición) y **Agregar producto** (tipo Bebida o Snack, nombre, precio, stock inicial y mililitros o categoría).
  - El identificador se asigna solo (P004, P005, …).
  - El producto nuevo se guarda en `productos.csv`, aparece de inmediato en la tabla, queda seleccionado y está disponible en Pedidos.
  - No se permiten dos productos con el mismo nombre (sin distinguir mayúsculas).
- El título "BOTILLERÍA" del panel lateral quedó centrado y un poco más grande.
- Nuevos `Bodega.agregar`, `Bodega.siguiente_id`, `Botilleria.registrar_producto` y `Controlador.registrar_producto`.

## v1.7 — Ventas actualizan los CSV, edición de productos y Registro Voucher
- Cada venta pagada actualiza **ambos CSV**: `productos.csv` (stock) y `clientes.csv` (nuevas columnas `compras` y `total_comprado`). Cancelar un pedido pagado revierte los dos. Un pago rechazado no cambia nada.
- Productos: botón **Activar edición / Desactivar edición**. Con la edición activa, al elegir una fila se puede cambiar nombre, precio, stock y mililitros (bebida) o categoría (snack). Se guarda en `productos.csv`.
  - El stock no puede quedar bajo las unidades ya reservadas en pedidos creados.
  - Los pedidos ya creados conservan el precio con que se agregó el producto.
- Nuevo módulo **Registro Voucher** al final del panel lateral: boleta del pedido pagado con datos del cliente, detalle de productos, medio y estado del pago, y la palabra **PAGADO!** centrada y en negrita en la última línea.
- Clientes: la tabla muestra `Compras` y `Total comprado`.
- Nuevo `modelo/voucher.py` (`Voucher`, `crear_voucher`). `Cliente` suma `registrar_compra` y `anular_compra`; `Producto` suma `actualizar`; `Botilleria` suma `editar_producto`.
- `crear_controlador(guardar=False)` reemplaza a `guardar_clientes=False` (la demo no modifica ningún CSV).
- Los pedidos y los vouchers no se guardan: el Registro Voucher muestra los pagados en la sesión actual. El stock y las compras sí quedan guardados.

## v1.6 — Estilo Editorial y datos en CSV
- Nueva apariencia (propuesta 3, Editorial): fondo papel cálido, títulos con fuente serif, secciones con rótulos en mayúsculas verdes, tablas con encabezados en mayúsculas y botones principales en verde oscuro.
- Panel lateral negro con enlaces verde claro (ya no son botones); el enlace activo se resalta y al pasar el cursor se subraya.
- Las fuentes se eligen según lo instalado: Source Serif 4 / Source Sans 3 si existen; si no, Georgia y Segoe UI (o equivalentes).
- `data/clientes.csv`: lista de clientes. Se lee al abrir y se guarda sola al registrar, editar o eliminar.
- `data/productos.csv`: catálogo y stock inicial de la bodega. Es de solo lectura: los productos y su stock ya no están escritos en el código.
- Nuevo `persistencia/repositorio_csv.py`. Si un CSV falta o tiene datos inválidos, la aplicación avisa qué archivo y qué fila fallan, y no se cae.
- La demo de consola lee los CSV pero no modifica `clientes.csv`.
- Los pedidos y el stock vendido siguen sin guardarse: al cerrar, el stock vuelve al valor del CSV.

## v1.5 — Editar y eliminar clientes
- La pantalla Clientes suma "Guardar cambios" y "Eliminar", como en FlashFood: al seleccionar una fila se carga el formulario y se habilitan los botones.
- `Cliente.actualizar` valida todo antes de cambiar: si un dato es inválido, el cliente queda igual.
- No se puede eliminar un cliente que tiene pedidos.
- Los pedidos ya creados conservan el descuento VIP con que se crearon, aunque el cliente cambie después.
- Persistencia JSON y módulos Repartidores y Seguimiento siguen fuera.

## v1.4 — Interfaz gráfica (Tkinter)
- Ventana principal con menú lateral "Módulos" y barra de menú, igual que FlashFood.
- Pantallas: Inicio, Productos (consulta), Clientes (registrar y consultar), Pedidos, Detalle del pedido y Pagos.
- Tablas con `ttk.Treeview`, avisos con `messagebox` y botones que se habilitan según el estado del pedido.
- `python -m botilleria` abre la ventana; la demo de consola pasa a `python -m botilleria.demo`.
- El controlador suma `reglas()` y `resumen()` para la pantalla de inicio.
- Sin persistencia todavía: los clientes y pedidos se pierden al cerrar la ventana.
- Probado con un Tkinter simulado; falta probarlo con la ventana real.

## v1.3 — Modelo en estilo FlashFood y controlador
- Modelo ajustado al estilo de FlashFood: `validacion.py` (devuelve el valor limpio), `formato.py` (`pesos`), `pago.py`, `pedido.py` y `sistema.py`.
- Cada clase guarda y carga con `a_diccionario()` y `desde_diccionario()`.
- Los estados usan una tabla de transiciones (`CREADO → PAGADO`, y `CANCELADO` desde ambos).
- El stock se descuenta en `Botilleria.pagar`, solo con el pago aprobado; la cancelación lo devuelve una sola vez.
- Nuevo `Controlador`: convierte el texto de la vista, arma el medio de pago y expone `acciones()` para habilitar botones.
- Los productos del catálogo son solo de consulta: la bodega es fija.
- `demo.py` ahora usa el controlador, como lo hará la vista.
- Persistencia y vista siguen vacías.
- Configuración de VS Code (`.vscode/`) para ejecutar con F5.

## v1.2 — Conversión de la v1.0 (Java) a Python
- Modelo del área de ventas traducido a Python dentro de `modelo/`, con el estilo de FlashFood.
- Nueva `validaciones.py` (equivale a la clase `Validaciones` de Java).
- `demo.py` reemplaza a `Main.java`; `python -m botilleria` ejecuta la demostración.
- La salida de la demo es idéntica a la de la v1.0 en Java.
- Persistencia, controlador y vista siguen vacíos.
- Datos de ejemplo por confirmar: P003 (Papas fritas) y los 355 ml de las cervezas.

## v1.1 — Estructura en Python
- Directorios y módulos emulando FlashFood (modelo, persistencia, controladores, vista, data y tests).

## v1.0 — Primera versión de prueba (Java)
- Área de ventas en Java con menú de demostración.
