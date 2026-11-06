"""Demostración sin ventanas: usa el Controlador igual que lo hará la vista.

Los números llegan como texto, porque así los entregará un formulario.
"""

from botilleria.controladores import Controlador, crear_controlador
from botilleria.modelo import Pedido, ReglaNegocioError
from botilleria.modelo.formato import pesos


def mostrar_bodega(controlador: Controlador, titulo: str) -> None:
    print(f"--- {titulo} ---")
    for producto in controlador.listar_productos():
        print(
            f"[{producto.id}] {producto.nombre} ({producto.detalle}) - {pesos(producto.precio)} "
            f"- Stock: {producto.stock} - Disponible: {controlador.stock_disponible(producto.id)}"
        )


def mostrar_pedido(controlador: Controlador, pedido: Pedido) -> None:
    for d in pedido.detalles:
        print(f"  {d.cantidad} x {d.nombre} ({pesos(d.precio_unitario)}) = {pesos(d.subtotal)}")
    print(
        f"  Subtotal: {pesos(pedido.subtotal)} | Descuento VIP: {pesos(pedido.descuento)} "
        f"| Total: {pesos(pedido.total)}"
    )


def intentar(descripcion: str, accion) -> None:
    """Ejecuta una acción que debería fallar y muestra el error sin cerrar el programa."""
    try:
        accion()
    except ReglaNegocioError as error:
        print(f"{descripcion}: {error}")


def main() -> None:
    controlador = crear_controlador(guardar=False)  # no modifica los CSV

    camila = controlador.registrar_cliente("Camila Soto", "+56911112222", "Av. Central 123", False)
    andres = controlador.registrar_cliente("Andrés Rojas", "+56933334444", "Los Aromos 45", True)

    mostrar_bodega(controlador, "Bodega inicial")

    print("\n--- Pedido de Camila (cliente normal) ---")
    pedido1 = controlador.crear_pedido(camila.id)
    controlador.agregar_producto(pedido1.id, "P001", "4")
    controlador.agregar_producto(pedido1.id, "P003", "2")
    mostrar_pedido(controlador, pedido1)

    rechazado = controlador.pagar(pedido1.id, "Tarjeta", True, "", "")
    print(f"Tarjeta: {rechazado.mensaje} | Estado: {pedido1.estado.etiqueta}")

    aprobado = controlador.pagar(pedido1.id, "Efectivo", False, "15000", "")
    print(f"Efectivo: {aprobado.mensaje} | Estado: {pedido1.estado.etiqueta}")

    intentar("Pago duplicado", lambda: controlador.pagar(pedido1.id, "Efectivo", False, "15000", ""))

    print("\n--- Pedido de Andrés (cliente VIP) ---")
    pedido2 = controlador.crear_pedido(andres.id)
    controlador.agregar_producto(pedido2.id, "P002", "6")
    mostrar_pedido(controlador, pedido2)
    print(controlador.pagar(pedido2.id, "Billetera digital", False, "", "10000").mensaje)

    print("\n--- Validación de entradas ---")
    pedido3 = controlador.crear_pedido(camila.id)
    intentar("Cantidad con letras", lambda: controlador.agregar_producto(pedido3.id, "P002", "abc"))
    intentar("Cantidad cero", lambda: controlador.agregar_producto(pedido3.id, "P002", "0"))
    intentar("Sin pedido", lambda: controlador.agregar_producto("", "P002", "1"))

    print("\n--- Stock comprometido entre pedidos ---")
    controlador.agregar_producto(pedido3.id, "P002", "3")
    pedido4 = controlador.crear_pedido(camila.id)
    intentar("Pedido 4", lambda: controlador.agregar_producto(pedido4.id, "P002", "2"))
    mostrar_bodega(controlador, "Bodega con pedido 3 creado")

    print("\n--- Cancelación del pedido de Andrés ---")
    controlador.cancelar(pedido2.id)
    print(
        f"Estado: {pedido2.estado.etiqueta} | Stock P002: "
        f"{controlador.obtener_producto('P002').stock} | Stock restituido: {pedido2.stock_restituido}"
    )
    intentar("Segunda cancelación", lambda: controlador.cancelar(pedido2.id))

    mostrar_bodega(controlador, "Bodega final")


if __name__ == "__main__":
    main()
