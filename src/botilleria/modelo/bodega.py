"""Bodega: catálogo de productos cargado desde productos.csv."""

from collections.abc import Iterable

from botilleria.modelo.errores import ReglaNegocioError
from botilleria.modelo.producto import Producto


class Bodega:
    """Catálogo cargado desde productos.csv.

    Se pueden agregar productos nuevos, pero no quitarlos. El stock baja con
    ventas pagadas, vuelve con las cancelaciones y puede corregirse al editar.
    """

    def __init__(self, productos: Iterable[Producto]):
        self._productos: dict[str, Producto] = {}
        for producto in productos:
            if producto.id in self._productos:
                raise ReglaNegocioError(f"Producto repetido: {producto.id}")
            self._productos[producto.id] = producto

    def agregar(self, producto: Producto) -> Producto:
        """Suma un producto nuevo; no puede repetir identificador ni nombre."""
        if producto.id in self._productos:
            raise ReglaNegocioError(f"Producto repetido: {producto.id}")
        if any(p.nombre.lower() == producto.nombre.lower() for p in self._productos.values()):
            raise ReglaNegocioError(f"Ya existe un producto llamado {producto.nombre}")
        self._productos[producto.id] = producto
        return producto

    def siguiente_id(self) -> str:
        """P001, P002... el primer número libre después del mayor existente."""
        numeros = [int(i[1:]) for i in self._productos if i[:1] == "P" and i[1:].isdigit()]
        return f"P{(max(numeros) if numeros else 0) + 1:03d}"

    def buscar(self, producto_id: str) -> Producto:
        if producto_id not in self._productos:
            raise ReglaNegocioError(f"No existe el producto {producto_id}")
        return self._productos[producto_id]

    def listar(self) -> tuple[Producto, ...]:
        return tuple(self._productos.values())
