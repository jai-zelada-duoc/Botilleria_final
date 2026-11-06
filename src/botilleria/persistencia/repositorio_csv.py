"""RepositorioCSV: lee y guarda clientes y productos en archivos CSV.

Ambos archivos se leen al abrir y se vuelven a guardar tras cada cambio
(registro o edición de clientes, ventas, cancelaciones y edición de productos).
"""

import csv
from pathlib import Path

from botilleria.modelo.cliente import Cliente
from botilleria.modelo.errores import PersistenciaError, ReglaNegocioError
from botilleria.modelo.producto import Bebida, Producto, Snack
from botilleria.rutas import CLIENTES_CSV, DATA, PRODUCTOS_CSV

COLUMNAS_CLIENTES = ("id", "nombre", "telefono", "direccion", "es_vip")
COLUMNAS_CLIENTES_GUARDADO = COLUMNAS_CLIENTES + ("compras", "total_comprado")
COLUMNAS_PRODUCTOS = ("id", "tipo", "nombre", "precio", "stock", "mililitros", "categoria")
_SI = {"si", "sí", "true", "1"}
_NO = {"no", "false", "0", ""}


class RepositorioCSV:
    def __init__(self, directorio: Path | str | None = None):
        self._directorio = Path(directorio) if directorio else DATA

    @property
    def ruta_clientes(self) -> Path:
        return self._directorio / CLIENTES_CSV

    @property
    def ruta_productos(self) -> Path:
        return self._directorio / PRODUCTOS_CSV

    # --- lectura ---

    def cargar_clientes(self) -> list[Cliente]:
        clientes = []
        identificadores = set()
        for numero, fila in self._leer(self.ruta_clientes, COLUMNAS_CLIENTES):
            try:
                if fila["id"] in identificadores:
                    raise PersistenciaError(
                        f"{self.ruta_clientes.name}, fila {numero}: identificador repetido {fila['id']!r}"
                    )
                clientes.append(
                    Cliente(
                        fila["id"],
                        fila["nombre"],
                        fila["telefono"],
                        fila["direccion"],
                        self._booleano(fila["es_vip"]),
                        int(fila.get("compras") or 0),
                        int(fila.get("total_comprado") or 0),
                    )
                )
                identificadores.add(fila["id"])
            except PersistenciaError:
                raise
            except ReglaNegocioError as error:
                raise PersistenciaError(
                    f"{self.ruta_clientes.name}, fila {numero}: {error}"
                ) from error
            except ValueError as error:
                raise PersistenciaError(
                    f"{self.ruta_clientes.name}, fila {numero}: "
                    "compras y total_comprado deben ser números enteros"
                ) from error
        return clientes

    def cargar_productos(self) -> list[Producto]:
        productos = []
        identificadores = set()
        nombres = set()
        for numero, fila in self._leer(self.ruta_productos, COLUMNAS_PRODUCTOS):
            try:
                producto = self._producto(fila)
                nombre_normalizado = producto.nombre.casefold()
                if producto.id in identificadores:
                    raise PersistenciaError(
                        f"{self.ruta_productos.name}, fila {numero}: identificador repetido {producto.id!r}"
                    )
                if nombre_normalizado in nombres:
                    raise PersistenciaError(
                        f"{self.ruta_productos.name}, fila {numero}: nombre de producto repetido "
                        f"{producto.nombre!r}"
                    )
                productos.append(producto)
                identificadores.add(producto.id)
                nombres.add(nombre_normalizado)
            except PersistenciaError:
                raise
            except ReglaNegocioError as error:
                raise PersistenciaError(
                    f"{self.ruta_productos.name}, fila {numero}: {error}"
                ) from error
            except ValueError as error:
                raise PersistenciaError(
                    f"{self.ruta_productos.name}, fila {numero}: "
                    "precio, stock y mililitros deben ser números enteros"
                ) from error
        if not productos:
            raise PersistenciaError(f"{self.ruta_productos.name} no tiene productos")
        return productos

    # --- escritura ---

    def guardar_clientes(self, clientes) -> None:
        try:
            self._directorio.mkdir(parents=True, exist_ok=True)
            with self.ruta_clientes.open("w", encoding="utf-8-sig", newline="") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(COLUMNAS_CLIENTES_GUARDADO)
                for c in clientes:
                    escritor.writerow(
                        [
                            c.id,
                            c.nombre,
                            c.telefono,
                            c.direccion,
                            "si" if c.es_vip else "no",
                            c.compras,
                            c.total_comprado,
                        ]
                    )
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo guardar {self.ruta_clientes.name}. "
                "Revisa que no esté abierto en otro programa."
            ) from error

    def guardar_productos(self, productos) -> None:
        try:
            self._directorio.mkdir(parents=True, exist_ok=True)
            with self.ruta_productos.open("w", encoding="utf-8-sig", newline="") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(COLUMNAS_PRODUCTOS)
                for p in productos:
                    datos = p.a_diccionario()
                    escritor.writerow(
                        [
                            datos["id"],
                            datos["tipo"],
                            datos["nombre"],
                            datos["precio"],
                            datos["stock"],
                            datos.get("mililitros", ""),
                            datos.get("categoria", ""),
                        ]
                    )
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo guardar {self.ruta_productos.name}. "
                "Revisa que no esté abierto en otro programa."
            ) from error

    # --- apoyo ---

    def _leer(self, ruta: Path, columnas: tuple[str, ...]):
        """Devuelve (número de fila, diccionario) por cada fila con datos."""
        try:
            with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
                lector = csv.DictReader(archivo)
                faltantes = [c for c in columnas if c not in (lector.fieldnames or [])]
                if faltantes:
                    raise PersistenciaError(
                        f"{ruta.name} no tiene las columnas: {', '.join(faltantes)}"
                    )
                filas = []
                for numero, fila in enumerate(lector, start=2):
                    if None in fila:
                        raise PersistenciaError(
                            f"{ruta.name}, fila {numero}: hay más valores que columnas en el encabezado"
                        )
                    if any((valor or "").strip() for valor in fila.values()):
                        filas.append(
                            (numero, {clave: (valor or "").strip() for clave, valor in fila.items()})
                        )
                return filas
        except FileNotFoundError as error:
            raise PersistenciaError(f"No se encontró {ruta}") from error
        except (OSError, UnicodeDecodeError, csv.Error) as error:
            raise PersistenciaError(f"No se pudo leer {ruta.name}: {error}") from error

    @staticmethod
    def _booleano(valor: str) -> bool:
        texto = valor.strip().lower()
        if texto in _SI:
            return True
        if texto in _NO:
            return False
        raise ReglaNegocioError("es_vip debe ser si o no")

    @staticmethod
    def _producto(fila: dict) -> Producto:
        tipo = fila["tipo"].lower()
        base = (fila["id"], fila["nombre"], int(fila["precio"]), int(fila["stock"]))
        if tipo == "bebida":
            return Bebida(*base, int(fila["mililitros"]))
        if tipo == "snack":
            return Snack(*base, fila["categoria"])
        raise ReglaNegocioError(f"Tipo de producto desconocido: {fila['tipo']!r}")
