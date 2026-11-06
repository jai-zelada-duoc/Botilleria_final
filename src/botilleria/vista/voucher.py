"""Registro Voucher: boleta final de los pedidos pagados."""

import tkinter as tk
from tkinter import ttk

from botilleria.modelo.voucher import Voucher
from botilleria.vista.comun import (
    CAMPO,
    FUENTES_MONO,
    LINEA,
    TINTA,
    Pantalla,
    configurar_combo,
    elegir_fuente,
    pesos,
    titulo,
)

ANCHO = 48  # caracteres por línea de la boleta


class RegistroVoucher(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._pedidos: dict[str, str] = {}
        titulo(self, "Registro Voucher")
        ttk.Label(
            self,
            text="Boleta de los pedidos pagados en esta sesión. Elige un pedido para ver su voucher.",
            wraplength=760,
        ).pack(anchor="w", pady=(0, 8))
        self.pedido = tk.StringVar()
        self.combo = ttk.Combobox(self, textvariable=self.pedido, state="readonly")
        self.combo.pack(fill="x")
        self.combo.bind("<<ComboboxSelected>>", lambda _evento: self.mostrar())

        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True, pady=(12, 0))
        familia = elegir_fuente(self, FUENTES_MONO, "Courier")
        self.texto = tk.Text(
            marco,
            width=ANCHO,
            wrap="none",
            state="disabled",
            background=CAMPO,
            foreground=TINTA,
            relief="flat",
            highlightthickness=1,
            highlightbackground=LINEA,
            padx=16,
            pady=16,
            font=(familia, 11),
        )
        self.texto.pack(anchor="n", fill="y", expand=True)
        self.texto.tag_configure("centro", justify="center")
        self.texto.tag_configure("negrita", font=(familia, 11, "bold"))
        self.texto.tag_configure("titulo", justify="center", font=(familia, 14, "bold"))
        self.texto.tag_configure("pagado", justify="center", font=(familia, 18, "bold"))

    def refrescar(self) -> None:
        actual = self.pedido.get()
        self._pedidos = {}
        etiquetas = []
        for pedido in self.controlador.pedidos_pagados():
            etiqueta = (
                f"{pedido.id} — {self.controlador.nombre_cliente(pedido.cliente_id)} "
                f"— {pesos(pedido.total)}"
            )
            self._pedidos[etiqueta] = pedido.id
            etiquetas.append(etiqueta)
        configurar_combo(self.combo, etiquetas, actual)
        self.mostrar()

    def mostrar(self) -> None:
        pedido_id = self._pedidos.get(self.pedido.get())
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        if not pedido_id:
            self.texto.insert("end", "No hay pedidos pagados.", "centro")
        else:
            self._dibujar(self.controlador.voucher(pedido_id))
        self.texto.configure(state="disabled")

    def _dibujar(self, v: Voucher) -> None:
        def linea(texto: str = "", etiqueta: str | None = None) -> None:
            self.texto.insert("end", texto + "\n", *([etiqueta] if etiqueta else []))

        def par(izquierda: str, derecha: str, etiqueta: str | None = None) -> None:
            espacio = max(1, ANCHO - len(izquierda) - len(derecha))
            linea(izquierda + " " * espacio + derecha, etiqueta)

        linea("BOTILLERÍA", "titulo")
        linea("COMPROBANTE DE VENTA", "centro")
        linea(f"N° {v.numero}", "centro")
        linea("=" * ANCHO)
        linea("CLIENTE", "negrita")
        linea(f"Nombre:    {v.cliente_nombre}")
        linea(f"Teléfono:  {v.cliente_telefono}")
        linea(f"Dirección: {v.cliente_direccion}")
        linea(f"Tipo:      {v.tipo_cliente}")
        linea("-" * ANCHO)
        linea("DETALLE", "negrita")
        for cantidad, nombre, _unitario, subtotal in v.lineas:
            izquierda = f"{cantidad} x {nombre}"
            derecha = pesos(subtotal)
            relleno = ANCHO - len(izquierda) - len(derecha) - 2
            linea(f"{izquierda} {'.' * max(2, relleno)} {derecha}")
        linea("-" * ANCHO)
        par("Subtotal", pesos(v.subtotal))
        if v.descuento:
            par("Descuento VIP", "-" + pesos(v.descuento))
        par("TOTAL", pesos(v.total), "negrita")
        linea("-" * ANCHO)
        linea("PAGO", "negrita")
        linea(f"Medio de pago:   {v.medio}")
        linea(f"Referencia:      {v.referencia}")
        linea(f"Estado del pago: {v.estado_pago}")
        linea("=" * ANCHO)
        linea()
        self.texto.insert("end", "PAGADO!", "pagado")
