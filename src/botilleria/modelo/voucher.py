"""Voucher: la boleta final de un pedido pagado."""

from dataclasses import dataclass

from botilleria.modelo.cliente import Cliente
from botilleria.modelo.errores import ReglaNegocioError
from botilleria.modelo.pedido import EstadoPedido, Pedido


@dataclass(frozen=True)
class Voucher:
    """Copia de solo lectura con todo lo que muestra la boleta."""

    numero: str
    cliente_nombre: str
    cliente_telefono: str
    cliente_direccion: str
    tipo_cliente: str
    lineas: tuple[tuple[int, str, int, int], ...]  # (cantidad, nombre, precio unitario, subtotal)
    subtotal: int
    descuento: int
    total: int
    medio: str
    referencia: str
    estado_pago: str


def crear_voucher(pedido: Pedido, cliente: Cliente) -> Voucher:
    """Solo los pedidos pagados tienen voucher."""
    if pedido.estado is not EstadoPedido.PAGADO or pedido.pago is None:
        raise ReglaNegocioError("Solo los pedidos pagados tienen voucher")
    pago = pedido.pago
    return Voucher(
        numero=pedido.id,
        cliente_nombre=cliente.nombre,
        cliente_telefono=cliente.telefono,
        cliente_direccion=cliente.direccion,
        tipo_cliente="VIP" if pedido.es_vip else "Normal",
        lineas=tuple(
            (d.cantidad, d.nombre, d.precio_unitario, d.subtotal) for d in pedido.detalles
        ),
        subtotal=pedido.subtotal,
        descuento=pedido.descuento,
        total=pedido.total,
        medio=pago.medio,
        referencia=pago.referencia,
        estado_pago="Aprobado" if pago.aprobado else "Rechazado",
    )
