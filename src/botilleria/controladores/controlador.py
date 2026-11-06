"""Controlador: recibe los eventos de la vista y los traduce al modelo.

La vista entrega texto (lo que el usuario escribe). Aquí se convierte y se
valida el formato; las reglas de negocio viven en el modelo.
"""

from botilleria.modelo import (
    Botilleria,
    Cliente,
    MetodoPago,
    PagoBilletera,
    PagoEfectivo,
    PagoTarjeta,
    Pedido,
    Producto,
    ReglaNegocioError,
    ResultadoPago,
    Voucher,
)
from botilleria.modelo.pedido import EstadoPedido
from botilleria.modelo.validacion import exigir_entero
from botilleria.persistencia import RepositorioCSV


class Controlador:
    """Si recibe un repositorio, guarda los CSV tras cada cambio."""

    def __init__(self, sistema: Botilleria, repositorio: RepositorioCSV | None = None):
        self._sistema = sistema
        self._repositorio = repositorio

    def _guardar_clientes(self) -> None:
        if self._repositorio is not None:
            self._repositorio.guardar_clientes(self._sistema.listar_clientes())

    def _guardar_productos(self) -> None:
        if self._repositorio is not None:
            self._repositorio.guardar_productos(self._sistema.listar_productos())

    def _guardar_ventas(self) -> None:
        """Una venta cambia el stock y las compras del cliente: se guardan ambos CSV."""
        self._guardar_productos()
        self._guardar_clientes()

    # --- productos ---

    def listar_productos(self) -> tuple[Producto, ...]:
        return self._sistema.listar_productos()

    def obtener_producto(self, producto_id: str) -> Producto:
        return self._sistema.obtener_producto(producto_id)

    def stock_disponible(self, producto_id: str) -> int:
        return self._sistema.stock_disponible(producto_id)

    def registrar_producto(
        self, tipo: str, nombre: str, precio: str, stock: str, extra: str
    ) -> Producto:
        """`tipo` es "bebida" o "snack". `extra` son los mililitros o la categoría."""
        if tipo not in ("bebida", "snack"):
            raise ReglaNegocioError("Elige el tipo de producto")
        extra_valor = self._entero(extra, "Mililitros", 1) if tipo == "bebida" else extra
        producto = self._sistema.registrar_producto(
            tipo,
            nombre,
            self._entero(precio, "Precio", 1),
            self._entero(stock, "Stock", 0),
            extra_valor,
        )
        self._guardar_productos()
        return producto

    def editar_producto(
        self, producto_id: str, nombre: str, precio: str, stock: str, extra: str
    ) -> Producto:
        """Recibe texto de la vista. `extra` son los mililitros o la categoría."""
        self._exigir(producto_id, "un producto")
        producto = self._sistema.obtener_producto(producto_id)
        extra_valor = (
            self._entero(extra, "Mililitros", 1) if producto.tipo == "bebida" else extra
        )
        editado = self._sistema.editar_producto(
            producto_id,
            nombre,
            self._entero(precio, "Precio", 1),
            self._entero(stock, "Stock", 0),
            extra_valor,
        )
        self._guardar_productos()
        return editado

    # --- clientes ---

    def listar_clientes(self) -> tuple[Cliente, ...]:
        return self._sistema.listar_clientes()

    def obtener_cliente(self, cliente_id: str) -> Cliente:
        return self._sistema.obtener_cliente(cliente_id)

    def nombre_cliente(self, cliente_id: str) -> str:
        return self._sistema.obtener_cliente(cliente_id).nombre

    def registrar_cliente(self, nombre: str, telefono: str, direccion: str, es_vip: bool) -> Cliente:
        if type(es_vip) is not bool:
            raise ReglaNegocioError("El indicador VIP debe ser sí o no")
        cliente = self._sistema.registrar_cliente(nombre, telefono, direccion, es_vip)
        self._guardar_clientes()
        return cliente

    def editar_cliente(
        self, cliente_id: str, nombre: str, telefono: str, direccion: str, es_vip: bool
    ) -> Cliente:
        self._exigir(cliente_id, "un cliente")
        if type(es_vip) is not bool:
            raise ReglaNegocioError("El indicador VIP debe ser sí o no")
        cliente = self._sistema.editar_cliente(cliente_id, nombre, telefono, direccion, es_vip)
        self._guardar_clientes()
        return cliente

    def eliminar_cliente(self, cliente_id: str) -> None:
        self._exigir(cliente_id, "un cliente")
        self._sistema.eliminar_cliente(cliente_id)
        self._guardar_clientes()

    # --- pedidos ---

    def listar_pedidos(self) -> tuple[Pedido, ...]:
        return self._sistema.listar_pedidos()

    def obtener_pedido(self, pedido_id: str) -> Pedido:
        return self._sistema.obtener_pedido(pedido_id)

    def crear_pedido(self, cliente_id: str) -> Pedido:
        self._exigir(cliente_id, "un cliente")
        return self._sistema.crear_pedido(cliente_id)

    def agregar_producto(self, pedido_id: str, producto_id: str, cantidad: str) -> Pedido:
        self._exigir(pedido_id, "un pedido")
        self._exigir(producto_id, "un producto")
        return self._sistema.agregar_producto(
            pedido_id, producto_id, self._entero(cantidad, "Cantidad", 1)
        )

    def quitar_producto(self, pedido_id: str, producto_id: str) -> Pedido:
        self._exigir(pedido_id, "un pedido")
        self._exigir(producto_id, "una línea del pedido")
        return self._sistema.quitar_producto(pedido_id, producto_id)

    def pagar(
        self,
        pedido_id: str,
        medio: str,
        rechazar: bool,
        monto: str,
        saldo: str,
    ) -> ResultadoPago:
        self._exigir(pedido_id, "un pedido")
        metodo = self._crear_medio(medio, rechazar, monto, saldo)
        resultado = self._sistema.pagar(pedido_id, metodo)
        if resultado.aprobado:
            self._guardar_ventas()
        return resultado

    def cancelar(self, pedido_id: str) -> Pedido:
        self._exigir(pedido_id, "un pedido")
        pedido = self._sistema.cancelar(pedido_id)
        if pedido.stock_restituido:
            self._guardar_ventas()
        return pedido

    def pedidos_pagados(self) -> tuple[Pedido, ...]:
        return self._sistema.pedidos_pagados()

    def voucher(self, pedido_id: str) -> Voucher:
        self._exigir(pedido_id, "un pedido")
        return self._sistema.voucher(pedido_id)

    def acciones(self, pedido_id: str) -> dict:
        """Qué botones puede habilitar la vista para este pedido."""
        pedido = self._sistema.obtener_pedido(pedido_id)
        creado = pedido.estado is EstadoPedido.CREADO
        return {
            "puede_editar_items": creado,
            "puede_pagar": creado and bool(pedido.detalles),
            "puede_cancelar": pedido.puede_cancelarse(),
        }

    # --- inicio ---

    def reglas(self) -> str:
        return (
            f"Cliente VIP: {Pedido.PORCENTAJE_VIP}% de descuento sobre el subtotal. "
            "El stock baja con cada venta pagada y vuelve si se cancela un pedido pagado; "
            "ambos cambios quedan guardados en los CSV."
        )

    def resumen(self) -> dict:
        pedidos = {estado.etiqueta: 0 for estado in EstadoPedido}
        for pedido in self._sistema.listar_pedidos():
            pedidos[pedido.estado.etiqueta] += 1
        productos = self._sistema.listar_productos()
        clientes = self._sistema.listar_clientes()
        return {
            "productos": len(productos),
            "unidades": sum(producto.stock for producto in productos),
            "clientes": len(clientes),
            "vip": sum(1 for cliente in clientes if cliente.es_vip),
            "pedidos": pedidos,
        }

    # --- apoyo ---

    def _crear_medio(self, medio: str, rechazar: bool, monto: str, saldo: str) -> MetodoPago:
        if medio == "Tarjeta":
            return PagoTarjeta(not rechazar)
        if medio == "Efectivo":
            return PagoEfectivo(self._entero(monto, "Monto recibido", 1))
        if medio == "Billetera digital":
            return PagoBilletera(self._entero(saldo, "Saldo", 0))
        raise ReglaNegocioError("Medio de pago no válido")

    @staticmethod
    def _exigir(valor: str, nombre: str) -> None:
        if not valor:
            raise ReglaNegocioError(f"Selecciona {nombre}")

    @staticmethod
    def _entero(valor: str, campo: str, minimo: int) -> int:
        try:
            numero = int(str(valor).strip())
        except ValueError as error:
            raise ReglaNegocioError(f"{campo} debe ser un número entero") from error
        return exigir_entero(numero, campo, minimo)


def crear_controlador(directorio=None, guardar: bool = True) -> Controlador:
    """Carga productos y clientes desde los CSV y arma el sistema.

    Con guardar=False los cambios quedan solo en memoria (demo).
    """
    repositorio = RepositorioCSV(directorio)
    sistema = Botilleria(repositorio.cargar_productos(), repositorio.cargar_clientes())
    return Controlador(sistema, repositorio if guardar else None)
