"""Botilleria: coordina bodega, clientes, pedidos y stock."""

from collections.abc import Iterable
from uuid import uuid4

from botilleria.modelo.bodega import Bodega
from botilleria.modelo.cliente import Cliente
from botilleria.modelo.errores import ReglaNegocioError
from botilleria.modelo.pago import MetodoPago, ResultadoPago
from botilleria.modelo.pedido import EstadoPedido, Pedido
from botilleria.modelo.producto import Bebida, Producto, Snack
from botilleria.modelo.validacion import exigir_entero
from botilleria.modelo.voucher import Voucher, crear_voucher


class Botilleria:
    """Aquí viven las reglas que involucran a varios objetos a la vez."""

    def __init__(self, productos: Iterable[Producto], clientes: Iterable[Cliente] = ()):
        self._bodega = Bodega(productos)
        self._clientes: dict[str, Cliente] = {c.id: c for c in clientes}
        self._pedidos: dict[str, Pedido] = {}
        self._medios: dict[str, MetodoPago] = {}

    # --- productos ---

    def listar_productos(self) -> tuple[Producto, ...]:
        return self._bodega.listar()

    def obtener_producto(self, producto_id: str) -> Producto:
        return self._bodega.buscar(producto_id)

    def registrar_producto(
        self, tipo: str, nombre: str, precio: int, stock: int, extra: object
    ) -> Producto:
        """Crea un Bebida o Snack con el siguiente identificador libre."""
        identificador = self._bodega.siguiente_id()
        if tipo == "bebida":
            producto = Bebida(identificador, nombre, precio, stock, extra)
        elif tipo == "snack":
            producto = Snack(identificador, nombre, precio, stock, extra)
        else:
            raise ReglaNegocioError("Elige el tipo de producto")
        return self._bodega.agregar(producto)

    def _comprometido(self, producto_id: str) -> int:
        """Unidades reservadas en pedidos creados que aún no se pagan."""
        return sum(
            pedido.cantidad_de(producto_id)
            for pedido in self._pedidos.values()
            if pedido.estado is EstadoPedido.CREADO
        )

    def stock_disponible(self, producto_id: str) -> int:
        """Stock menos lo ya comprometido en pedidos creados que aún no se pagan."""
        return self.obtener_producto(producto_id).stock - self._comprometido(producto_id)

    def editar_producto(
        self, producto_id: str, nombre: str, precio: int, stock: int, extra: object
    ) -> Producto:
        """Edita un producto. Los pedidos ya creados conservan el precio con que se agregó.

        El stock no puede quedar bajo lo ya reservado en pedidos creados.
        """
        producto = self.obtener_producto(producto_id)
        comprometido = self._comprometido(producto_id)
        if type(stock) is int and 0 <= stock < comprometido:
            raise ReglaNegocioError(
                f"El stock no puede ser menor que {comprometido}, "
                "las unidades ya reservadas en pedidos creados"
            )
        producto.actualizar(nombre, precio, stock, extra)
        return producto

    # --- clientes ---

    def listar_clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes.values())

    def obtener_cliente(self, cliente_id: str) -> Cliente:
        if cliente_id not in self._clientes:
            raise ReglaNegocioError("El cliente no existe")
        return self._clientes[cliente_id]

    def registrar_cliente(self, nombre: str, telefono: str, direccion: str, es_vip: bool) -> Cliente:
        cliente = Cliente(f"cli-{uuid4().hex[:8]}", nombre, telefono, direccion, es_vip)
        self._clientes[cliente.id] = cliente
        return cliente

    def editar_cliente(
        self, cliente_id: str, nombre: str, telefono: str, direccion: str, es_vip: bool
    ) -> Cliente:
        """Los pedidos ya creados conservan el descuento con que se crearon."""
        cliente = self.obtener_cliente(cliente_id)
        cliente.actualizar(nombre, telefono, direccion, es_vip)
        return cliente

    def eliminar_cliente(self, cliente_id: str) -> None:
        self.obtener_cliente(cliente_id)
        if any(pedido.cliente_id == cliente_id for pedido in self._pedidos.values()):
            raise ReglaNegocioError("No se puede eliminar un cliente que tiene pedidos")
        del self._clientes[cliente_id]

    # --- pedidos ---

    def listar_pedidos(self) -> tuple[Pedido, ...]:
        return tuple(self._pedidos.values())

    def obtener_pedido(self, pedido_id: str) -> Pedido:
        if pedido_id not in self._pedidos:
            raise ReglaNegocioError("El pedido no existe")
        return self._pedidos[pedido_id]

    def crear_pedido(self, cliente_id: str) -> Pedido:
        cliente = self.obtener_cliente(cliente_id)
        pedido = Pedido(f"ped-{uuid4().hex[:8]}", cliente.id, cliente.es_vip)
        self._pedidos[pedido.id] = pedido
        return pedido

    def agregar_producto(self, pedido_id: str, producto_id: str, cantidad: int) -> Pedido:
        pedido = self.obtener_pedido(pedido_id)
        producto = self.obtener_producto(producto_id)
        cantidad = exigir_entero(cantidad, "Cantidad", minimo=1)
        disponible = self.stock_disponible(producto_id)
        if cantidad > disponible:
            raise ReglaNegocioError(
                f"Stock insuficiente de {producto.nombre}. Disponible: {disponible}"
            )
        pedido.agregar(producto, cantidad)
        return pedido

    def quitar_producto(self, pedido_id: str, producto_id: str) -> Pedido:
        pedido = self.obtener_pedido(pedido_id)
        pedido.quitar(producto_id)
        return pedido

    def pedidos_pagados(self) -> tuple[Pedido, ...]:
        return tuple(p for p in self._pedidos.values() if p.estado is EstadoPedido.PAGADO)

    def voucher(self, pedido_id: str) -> Voucher:
        pedido = self.obtener_pedido(pedido_id)
        return crear_voucher(pedido, self.obtener_cliente(pedido.cliente_id))

    # --- pago y cancelación ---

    def pagar(self, pedido_id: str, metodo: MetodoPago) -> ResultadoPago:
        """Cobra y, solo si el pago se aprueba, descuenta el stock una vez."""
        pedido = self.obtener_pedido(pedido_id)
        resultado = pedido.cobrar(metodo)
        if not resultado.aprobado:
            return resultado

        try:
            for detalle in pedido.detalles:
                producto = self.obtener_producto(detalle.producto_id)
                if detalle.cantidad > producto.stock:
                    raise ReglaNegocioError(
                        f"Stock insuficiente de {producto.nombre}. Disponible: {producto.stock}"
                    )
        except ReglaNegocioError:
            metodo.anular(resultado)
            raise

        for detalle in pedido.detalles:
            self.obtener_producto(detalle.producto_id).descontar(detalle.cantidad)

        pedido.confirmar_pago(resultado)
        self._medios[pedido.id] = metodo
        self._clientes[pedido.cliente_id].registrar_compra(pedido.total)
        return resultado

    def cancelar(self, pedido_id: str) -> Pedido:
        """Cancela; si ya estaba pagado, devuelve el stock una sola vez y anula el cobro."""
        pedido = self.obtener_pedido(pedido_id)
        pedido.cancelar()

        if pedido.stock_descontado and not pedido.stock_restituido:
            for detalle in pedido.detalles:
                self.obtener_producto(detalle.producto_id).reponer(detalle.cantidad)
            pedido.marcar_stock_restituido()
            self._medios[pedido.id].anular(pedido.pago)
            self._clientes[pedido.cliente_id].anular_compra(pedido.total)

        return pedido
