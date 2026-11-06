"""Piezas compartidas por las pantallas."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from botilleria.modelo.errores import PersistenciaError, ReglaNegocioError
from botilleria.modelo.formato import pesos

# Paleta "Editorial": papel cálido, tinta oscura, panel negro con enlaces verde claro.
PAPEL = "#F7F4EC"
CAMPO = "#FFFDF8"
TINTA = "#1C1C1A"
GRIS = "#5A5A55"
LINEA = "#CFC9BA"
VERDE = "#14532D"
VERDE_TEXTO = "#166534"
SELECCION = "#DCFCE7"
NEGRO = "#0B0B0B"
ENLACE = "#86EFAC"
ACTIVO = "#18201B"

FUENTES_TEXTO = ("Source Sans 3", "Segoe UI", "Helvetica Neue", "Arial")
FUENTES_TITULO = ("Source Serif 4", "Georgia", "Palatino Linotype", "Times New Roman")

MODULOS = (
    ("inicio", "Inicio"),
    ("productos", "Productos"),
    ("clientes", "Clientes"),
    ("pedidos", "Pedidos"),
    ("detalle", "Detalle del pedido"),
    ("pagos", "Pagos"),
    ("voucher", "Registro Voucher"),
)

FUENTES_MONO = ("Consolas", "Courier New", "Menlo", "DejaVu Sans Mono")


def elegir_fuente(raiz: tk.Misc, preferidas: tuple[str, ...], respaldo: str) -> str:
    """Primera fuente de la lista que exista en este computador."""
    try:
        disponibles = {familia.lower() for familia in tkfont.families(raiz)}
    except tk.TclError:
        return respaldo
    for familia in preferidas:
        if familia.lower() in disponibles:
            return familia
    return respaldo


def informar(parent: tk.Misc, titulo: str, mensaje: str) -> None:
    messagebox.showinfo(titulo, mensaje, parent=parent)


def mostrar_error(parent: tk.Misc, mensaje: str) -> None:
    messagebox.showerror("No se pudo completar", mensaje, parent=parent)


def pedir_confirmacion(parent: tk.Misc, titulo: str, mensaje: str) -> bool:
    return bool(messagebox.askyesno(titulo, mensaje, parent=parent))


def titulo(parent: tk.Misc, texto: str) -> ttk.Label:
    etiqueta = ttk.Label(parent, text=texto, style="Titulo.TLabel")
    etiqueta.pack(anchor="w", pady=(0, 12))
    return etiqueta


def crear_tabla(
    parent: tk.Misc,
    columnas: tuple[str, ...],
    encabezados: tuple[str, ...],
    anchos: tuple[int, ...],
    altura: int = 8,
) -> tuple[ttk.Frame, ttk.Treeview]:
    marco = ttk.Frame(parent)
    tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=altura, selectmode="browse")
    scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    for columna, encabezado, ancho in zip(columnas, encabezados, anchos):
        tabla.heading(columna, text=encabezado.upper())
        anchor = "e" if columna in {"precio", "stock", "disponible", "cantidad", "subtotal", "total", "compras"} else "w"
        tabla.column(columna, width=ancho, anchor=anchor)
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")
    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)
    return marco, tabla


def configurar_combo(combo: ttk.Combobox, etiquetas: list[str], actual: str) -> None:
    combo["values"] = etiquetas
    if actual in etiquetas:
        combo.set(actual)
    elif etiquetas:
        combo.current(0)
    else:
        combo.set("")


class Pantalla(ttk.Frame):
    """Las pantallas llaman al controlador. Las reglas viven en el modelo."""

    def __init__(self, master: tk.Misc, controlador):
        super().__init__(master, padding=16)
        self.controlador = controlador

    def refrescar(self) -> None:
        return None

    def ejecutar(self, accion):
        try:
            return True, accion()
        except (ReglaNegocioError, PersistenciaError) as error:
            mostrar_error(self.winfo_toplevel(), str(error))
            return False, None


__all__ = [
    "CAMPO",
    "FUENTES_MONO",
    "LINEA",
    "MODULOS",
    "Pantalla",
    "configurar_combo",
    "crear_tabla",
    "elegir_fuente",
    "informar",
    "mostrar_error",
    "pedir_confirmacion",
    "pesos",
    "TINTA",
    "titulo",
]
