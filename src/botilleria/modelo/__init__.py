"""Modelo de dominio. No importa Tkinter."""

from botilleria.modelo.bodega import Bodega
from botilleria.modelo.cliente import Cliente
from botilleria.modelo.errores import PersistenciaError, ReglaNegocioError
from botilleria.modelo.pago import (
    MetodoPago,
    PagoBilletera,
    PagoEfectivo,
    PagoTarjeta,
    ResultadoPago,
)
from botilleria.modelo.pedido import DetallePedido, EstadoPedido, Pedido
from botilleria.modelo.producto import Bebida, Producto, Snack
from botilleria.modelo.sistema import Botilleria
from botilleria.modelo.voucher import Voucher, crear_voucher

__all__ = [
    "Bebida",
    "Bodega",
    "Botilleria",
    "Cliente",
    "DetallePedido",
    "EstadoPedido",
    "MetodoPago",
    "PagoBilletera",
    "PagoEfectivo",
    "PagoTarjeta",
    "Pedido",
    "PersistenciaError",
    "Producto",
    "ReglaNegocioError",
    "ResultadoPago",
    "Snack",
    "Voucher",
    "crear_voucher",
]
