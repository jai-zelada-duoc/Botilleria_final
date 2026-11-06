"""Pantalla de inicio: resumen de la operación y fichas de acceso a los módulos."""

import tkinter as tk
from tkinter import ttk

from botilleria.vista.comun import (
    ENLACE,
    GRIS,
    LINEA,
    MODULOS,
    NEGRO,
    PAPEL,
    TINTA,
    FUENTES_TEXTO,
    FUENTES_TITULO,
    Pantalla,
    elegir_fuente,
    titulo,
)

DESCRIPCIONES = {
    "productos": "stock, altas y edición",
    "clientes": "registro y compras",
    "pedidos": "crear y agregar",
    "detalle": "líneas y totales",
    "pagos": "procesar el cobro",
    "voucher": "boleta final",
}
GRIS_FICHA = "#9CA39E"


class Inicio(Pantalla):
    def __init__(self, master, controlador, navegar):
        super().__init__(master, controlador)
        self._navegar = navegar
        titulo(self, "Botillería")
        ttk.Label(
            self,
            text="Registra clientes, arma pedidos con los productos de la bodega y cóbralos.",
            wraplength=760,
        ).pack(anchor="w")
        self.reglas = ttk.Label(self, wraplength=760)
        self.reglas.pack(anchor="w", pady=(8, 12))

        # Cifras grandes entre una línea gruesa arriba y una fina abajo.
        tinta = tk.Frame(self, background=TINTA, height=2)
        tinta.pack(fill="x")
        cifras = tk.Frame(self, background=PAPEL)
        cifras.pack(fill="x")
        tk.Frame(self, background=LINEA, height=1).pack(fill="x", pady=(0, 14))
        familia = elegir_fuente(self, FUENTES_TITULO, "Times")
        self._sans = elegir_fuente(self, FUENTES_TEXTO, "Helvetica")
        self._cifras: dict[str, tuple[tk.Label, tk.Label]] = {}
        for columna, (clave, rotulo) in enumerate(
            (("productos", "PRODUCTOS EN BODEGA"), ("clientes", "CLIENTES"), ("pedidos", "PEDIDOS"))
        ):
            bloque = tk.Frame(cifras, background=PAPEL)
            bloque.grid(row=0, column=columna, sticky="nsew", padx=(0 if columna == 0 else 20, 20), pady=12)
            numero = tk.Label(bloque, background=PAPEL, foreground=TINTA, font=(familia, 34, "bold"), anchor="w")
            numero.pack(anchor="w")
            tk.Label(
                bloque, text=rotulo, background=PAPEL, foreground=TINTA, font=(self._sans, 9, "bold"), anchor="w"
            ).pack(anchor="w")
            detalle = tk.Label(bloque, background=PAPEL, foreground=GRIS, anchor="w")
            detalle.pack(anchor="w")
            self._cifras[clave] = (numero, detalle)
            cifras.columnconfigure(columna, weight=1, uniform="cifras")

        ttk.Label(self, text="MÓDULOS", style="Rotulo.TLabel").pack(anchor="w", pady=(0, 8))
        fichas = tk.Frame(self, background=PAPEL)
        fichas.pack(fill="x")
        visibles = [(clave, etiqueta) for clave, etiqueta in MODULOS if clave != "inicio"]
        for indice, (clave, etiqueta) in enumerate(visibles):
            self._crear_ficha(fichas, clave, etiqueta).grid(
                row=indice // 3, column=indice % 3, sticky="nsew", padx=5, pady=5
            )
        for columna in range(3):
            fichas.columnconfigure(columna, weight=1, uniform="fichas")

    def _crear_ficha(self, padre: tk.Misc, clave: str, etiqueta: str) -> tk.Frame:
        """Ficha negra con texto verde claro; toda la ficha es clicable."""
        ficha = tk.Frame(padre, background=NEGRO, cursor="hand2")
        texto = tk.Frame(ficha, background=NEGRO)
        texto.pack(side="left", fill="both", expand=True, padx=16, pady=14)
        nombre = tk.Label(texto, text=etiqueta, background=NEGRO, foreground=ENLACE, anchor="w", font=(self._sans, 11, "bold"))
        nombre.pack(anchor="w")
        descripcion = tk.Label(
            texto, text=DESCRIPCIONES.get(clave, ""), background=NEGRO, foreground=GRIS_FICHA, anchor="w"
        )
        descripcion.pack(anchor="w")
        flecha = tk.Label(ficha, text="→", background=NEGRO, foreground=ENLACE, font=(self._sans, 14))
        flecha.pack(side="right", padx=16)
        for widget in (ficha, texto, nombre, descripcion, flecha):
            widget.bind("<Button-1>", lambda _evento, destino=clave: self._navegar(destino))
        return ficha

    def refrescar(self) -> None:
        self.reglas.configure(text=self.controlador.reglas())
        datos = self.controlador.resumen()
        pedidos = datos["pedidos"]
        total_pedidos = sum(pedidos.values())
        valores = {
            "productos": (datos["productos"], f"{datos['unidades']} unidades en stock"),
            "clientes": (datos["clientes"], f"{datos['vip']} son VIP"),
            "pedidos": (
                total_pedidos,
                " · ".join(f"{cantidad} {estado.lower()}s" for estado, cantidad in pedidos.items()),
            ),
        }
        for clave, (cifra, texto) in valores.items():
            self._cifras[clave][0].configure(text=str(cifra))
            self._cifras[clave][1].configure(text=texto)
