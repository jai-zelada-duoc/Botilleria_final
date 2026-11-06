# Botillería — Área de ventas (Python) — Versión 1.8.1

Área de ventas de una botillería con POO.

## Ejecutar

Requiere Python 3.12 o superior con Tkinter. Desde la carpeta que contiene `src`:

```bash
python main.py
```

También se puede ejecutar como módulo:

```powershell
$env:PYTHONPATH="src"; python -m botilleria
```

En CMD: `set PYTHONPATH=src && python -m botilleria`. En Mac o Linux: `PYTHONPATH=src python3 -m botilleria`.

Se abre la ventana con el menú lateral. También funciona con **F5** en VS Code, abriendo la carpeta que contiene `src` y eligiendo "Botillería (ventana)".

La demostración sin ventanas se ejecuta con `python -m botilleria.demo` (con el mismo `PYTHONPATH`).

### Comprobar Tkinter

```bash
python -m tkinter
```

Debe abrir una ventanita de prueba. Si dice `No module named tkinter`:

- **Windows:** vuelve a ejecutar el instalador de Python, elige *Modify* y marca *tcl/tk and IDLE*.
- **Linux (Debian/Ubuntu):** `sudo apt install python3-tk`.
- **Mac:** instala Python desde python.org, o `brew install python-tk`.

### Primer uso

Al abrir, ya hay tres clientes de ejemplo y el catálogo de la bodega cargados desde `data/`:

1. **Clientes:** registra, edita o elimina. Los cambios se guardan solos en `clientes.csv`. No se puede eliminar un cliente con pedidos.
2. **Pedidos:** elige el cliente, crea el pedido y agrega productos.
3. **Pagos:** elige el pedido, el medio de pago y procésalo. Al aprobarse, se actualizan `productos.csv` y `clientes.csv`.
4. **Registro Voucher:** muestra la boleta del pedido pagado, terminada en **PAGADO!**.
5. **Productos:** la pestaña *Productos en bodega* muestra el stock y, con **Activar edición**, permite cambiar nombre, precio, stock y detalle. La pestaña *Agregar producto* crea productos nuevos (se guardan en `productos.csv`).
6. **Detalle del pedido** muestra las líneas y los totales.

## Datos (carpeta `data/`)

| Archivo | Contenido | Uso |
| --- | --- | --- |
| `clientes.csv` | `id, nombre, telefono, direccion, es_vip, compras, total_comprado` (`es_vip`: `si` o `no`) | Se lee al abrir; se guarda al registrar, editar, eliminar, vender o cancelar |
| `productos.csv` | `id, tipo, nombre, precio, stock, mililitros, categoria` | Se lee al abrir; se guarda al vender, cancelar o editar un producto |

En `productos.csv`, `tipo` es `bebida` (usa `mililitros`) o `snack` (usa `categoria`). Para agregar un producto usa la pestaña *Agregar producto*, y para cambiar uno existente el botón de edición. Quitar productos solo se puede editando el archivo con el Bloc de notas y la aplicación cerrada. Si `compras` y `total_comprado` faltan en `clientes.csv`, se leen como 0. Si lo abres con Excel, ten cuidado con los teléfonos que empiezan con `+`.

Los pedidos y los vouchers no se guardan: el Registro Voucher muestra los pedidos pagados en la sesión actual. El stock vendido y las compras de cada cliente sí quedan en los CSV.

## Estructura

```text
src/botilleria/modelo/          entidades y reglas de negocio (sin Tkinter)
src/botilleria/persistencia/    lectura y escritura de los CSV
src/botilleria/controladores/   traducción de la interfaz al modelo
src/botilleria/vista/           ventanas Tkinter y ttk
data/                           clientes.csv y productos.csv
tests/                          pruebas de regresión con unittest
```

## Clases del modelo

| Módulo | Clases |
| --- | --- |
| `producto.py` | `Producto` (abstracta), `Bebida`, `Snack` |
| `bodega.py` | `Bodega`: catálogo de productos (cargado desde el CSV; permite agregar) |
| `cliente.py` | `Cliente`, con indicador VIP y compras acumuladas |
| `pedido.py` | `EstadoPedido`, `DetallePedido`, `Pedido` |
| `pago.py` | `MetodoPago` (abstracta), `PagoTarjeta`, `PagoEfectivo`, `PagoBilletera`, `ResultadoPago` |
| `voucher.py` | `Voucher` (boleta de solo lectura), `crear_voucher` |
| `sistema.py` | `Botilleria`: coordina bodega, clientes, pedidos y stock |
| `errores.py`, `validacion.py`, `formato.py` | Errores, validaciones y formato de pesos |
| `controladores/controlador.py` | `Controlador`: traduce lo que escribe el usuario al modelo |

## Estados

```text
CREADO → PAGADO
   └──────→ CANCELADO   (también desde PAGADO)
```

## Reglas

1. No se agrega una cantidad mayor al stock, contando lo ya comprometido en otros pedidos creados.
2. El stock nunca queda negativo.
3. Un pedido puede tener varios productos; el precio de cada línea queda congelado.
4. Total = subtotal − descuento. El cliente VIP tiene 10% de descuento.
5. Un pedido no se paga dos veces. Un pago rechazado no confirma la compra ni descuenta stock.
6. El stock se descuenta una sola vez, al aprobarse el pago. Si no se puede, el cobro se anula.
7. Cancelar un pedido pagado devuelve el stock una sola vez y anula el cobro.
