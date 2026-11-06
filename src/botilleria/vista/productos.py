"""Productos de la bodega: catálogo con edición y pestaña para agregar productos nuevos."""

import tkinter as tk
from tkinter import ttk

from botilleria.vista.comun import Pantalla, crear_tabla, informar, mostrar_error, pesos, titulo


class Productos(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._producto_id: str | None = None
        self._editando = False
        titulo(self, "Productos")
        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True)
        self.pestana_catalogo = ttk.Frame(self.pestanas, padding=12)
        self.pestana_alta = ttk.Frame(self.pestanas, padding=12)
        self.pestanas.add(self.pestana_catalogo, text="Productos en bodega")
        self.pestanas.add(self.pestana_alta, text="Agregar producto")
        self._crear_catalogo(self.pestana_catalogo)
        self._crear_alta(self.pestana_alta)
        self.limpiar()
        self.limpiar_alta()

    def _crear_catalogo(self, pestana: ttk.Frame) -> None:
        ttk.Label(
            pestana,
            text=(
                "Disponible es el stock que aún se puede agregar a pedidos creados. "
                "Activa la edición para cambiar nombre, precio, stock y detalle."
            ),
            wraplength=740,
        ).pack(anchor="w", pady=(0, 8))

        barra = ttk.Frame(pestana)
        barra.pack(fill="x", pady=(0, 8))
        self.boton_edicion = ttk.Button(barra, text="Activar edición", command=self.alternar_edicion)
        self.boton_edicion.pack(side="left")

        self.formulario = ttk.LabelFrame(pestana, text="EDITAR PRODUCTO", padding=12)
        self.nombre = tk.StringVar()
        self.precio = tk.StringVar()
        self.stock = tk.StringVar()
        self.extra = tk.StringVar()
        self.etiqueta_extra = ttk.Label(self.formulario, text="Detalle")
        for fila, texto, variable in (
            (0, "Nombre", self.nombre),
            (1, "Precio", self.precio),
            (2, "Stock", self.stock),
        ):
            ttk.Label(self.formulario, text=texto).grid(row=fila, column=0, sticky="w", pady=4)
            ttk.Entry(self.formulario, textvariable=variable).grid(
                row=fila, column=1, sticky="ew", padx=(8, 0), pady=4
            )
        self.etiqueta_extra.grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(self.formulario, textvariable=self.extra).grid(
            row=3, column=1, sticky="ew", padx=(8, 0), pady=4
        )
        acciones = ttk.Frame(self.formulario)
        acciones.grid(row=4, column=1, sticky="e", pady=(8, 0))
        self.boton_guardar = ttk.Button(
            acciones, text="Guardar cambios", style="Primario.TButton", command=self.guardar
        )
        self.boton_limpiar = ttk.Button(acciones, text="Limpiar", command=self.limpiar)
        self.boton_guardar.pack(side="left", padx=(0, 8))
        self.boton_limpiar.pack(side="left")
        self.formulario.columnconfigure(1, weight=1)

        marco, self.tabla = crear_tabla(
            pestana,
            ("tipo", "nombre", "precio", "stock", "disponible", "detalle"),
            ("Tipo", "Nombre", "Precio", "Stock", "Disponible", "Detalle"),
            (100, 220, 110, 80, 100, 160),
        )
        marco.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

    def _crear_alta(self, pestana: ttk.Frame) -> None:
        ttk.Label(
            pestana,
            text=(
                "Agrega un producto nuevo a la bodega. Se guarda en productos.csv y aparece "
                "de inmediato en el catálogo y en Pedidos. El identificador se asigna solo."
            ),
            wraplength=740,
        ).pack(anchor="w", pady=(0, 8))
        alta = ttk.LabelFrame(pestana, text="NUEVO PRODUCTO", padding=12)
        alta.pack(fill="x")
        self.alta_tipo = tk.StringVar(value="Bebida")
        self.alta_nombre = tk.StringVar()
        self.alta_precio = tk.StringVar()
        self.alta_stock = tk.StringVar()
        self.alta_extra = tk.StringVar()
        ttk.Label(alta, text="Tipo").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_tipo = ttk.Combobox(
            alta, textvariable=self.alta_tipo, values=("Bebida", "Snack"), state="readonly"
        )
        self.combo_tipo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda _evento: self._rotular_alta())
        for fila, texto, variable in (
            (1, "Nombre", self.alta_nombre),
            (2, "Precio", self.alta_precio),
            (3, "Stock inicial", self.alta_stock),
        ):
            ttk.Label(alta, text=texto).grid(row=fila, column=0, sticky="w", pady=4)
            ttk.Entry(alta, textvariable=variable).grid(row=fila, column=1, sticky="ew", padx=(8, 0), pady=4)
        self.etiqueta_alta_extra = ttk.Label(alta, text="Mililitros")
        self.etiqueta_alta_extra.grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(alta, textvariable=self.alta_extra).grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=4)
        acciones = ttk.Frame(alta)
        acciones.grid(row=5, column=1, sticky="e", pady=(8, 0))
        ttk.Button(acciones, text="Agregar producto", style="Primario.TButton", command=self.agregar).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(acciones, text="Limpiar", command=self.limpiar_alta).pack(side="left")
        alta.columnconfigure(1, weight=1)

    def _rotular_alta(self) -> None:
        self.etiqueta_alta_extra.configure(
            text="Mililitros" if self.alta_tipo.get() == "Bebida" else "Categoría"
        )

    def limpiar_alta(self) -> None:
        self.alta_tipo.set("Bebida")
        for variable in (self.alta_nombre, self.alta_precio, self.alta_stock, self.alta_extra):
            variable.set("")
        self._rotular_alta()

    def agregar(self) -> None:
        tipo = "bebida" if self.alta_tipo.get() == "Bebida" else "snack"
        ok, producto = self.ejecutar(
            lambda: self.controlador.registrar_producto(
                tipo,
                self.alta_nombre.get(),
                self.alta_precio.get(),
                self.alta_stock.get(),
                self.alta_extra.get(),
            )
        )
        if not ok:
            return
        informar(
            self.winfo_toplevel(),
            "Producto agregado",
            f"{producto.nombre} quedó en la bodega y guardado en productos.csv.",
        )
        self.limpiar_alta()
        self._producto_id = producto.id
        self.refrescar()
        self.pestanas.select(self.pestana_catalogo)
        self.tabla.see(producto.id)

    def refrescar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for producto in self.controlador.listar_productos():
            self.tabla.insert(
                "",
                "end",
                iid=producto.id,
                values=(
                    producto.tipo_visible,
                    producto.nombre,
                    pesos(producto.precio),
                    producto.stock,
                    self.controlador.stock_disponible(producto.id),
                    producto.detalle,
                ),
            )
        if self._producto_id and self.tabla.exists(self._producto_id):
            self.tabla.selection_set(self._producto_id)

    def alternar_edicion(self) -> None:
        self._editando = not self._editando
        if self._editando:
            self.formulario.pack(fill="x", pady=(0, 8), before=self.tabla.master)
            self.boton_edicion.configure(text="Desactivar edición")
            self.al_seleccionar()
        else:
            self.formulario.pack_forget()
            self.boton_edicion.configure(text="Activar edición")
            self.limpiar()

    def al_seleccionar(self, _evento=None) -> None:
        if not self._editando:
            return
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        producto = self.controlador.obtener_producto(seleccion[0])
        self._producto_id = producto.id
        self.nombre.set(producto.nombre)
        self.precio.set(str(producto.precio))
        self.stock.set(str(producto.stock))
        if producto.tipo == "bebida":
            self.etiqueta_extra.configure(text="Mililitros")
            self.extra.set(str(producto.mililitros))
        else:
            self.etiqueta_extra.configure(text="Categoría")
            self.extra.set(producto.categoria)
        self.boton_guardar.configure(state="normal")

    def limpiar(self) -> None:
        self._producto_id = None
        for variable in (self.nombre, self.precio, self.stock, self.extra):
            variable.set("")
        self.etiqueta_extra.configure(text="Detalle")
        self.boton_guardar.configure(state="disabled")
        if self.tabla.selection():
            self.tabla.selection_remove(*self.tabla.selection())

    def guardar(self) -> None:
        if not self._producto_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona el producto que quieres editar.")
            return
        producto_id = self._producto_id
        ok, _producto = self.ejecutar(
            lambda: self.controlador.editar_producto(
                producto_id, self.nombre.get(), self.precio.get(), self.stock.get(), self.extra.get()
            )
        )
        if not ok:
            return
        informar(self.winfo_toplevel(), "Producto actualizado", "Los cambios quedaron guardados en productos.csv.")
        self.refrescar()
