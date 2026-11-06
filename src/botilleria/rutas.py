"""Rutas de las carpetas y archivos del proyecto."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "data"

CLIENTES_CSV = "clientes.csv"
PRODUCTOS_CSV = "productos.csv"
