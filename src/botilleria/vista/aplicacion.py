"""Ventana principal, panel lateral de enlaces y estilo visual."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from botilleria.controladores.controlador import Controlador, crear_controlador
from botilleria.modelo.errores import PersistenciaError
from botilleria.vista.clientes import Clientes
from botilleria.vista.comun import (
    ACTIVO,
    CAMPO,
    ENLACE,
    FUENTES_TEXTO,
    FUENTES_TITULO,
    GRIS,
    LINEA,
    MODULOS,
    NEGRO,
    PAPEL,
    SELECCION,
    TINTA,
    VERDE,
    VERDE_TEXTO,
    elegir_fuente,
    mostrar_error,
)
from botilleria.vista.detalle import Detalle
from botilleria.vista.inicio import Inicio
from botilleria.vista.pagos import Pagos
from botilleria.vista.pedidos import Pedidos
from botilleria.vista.productos import Productos
from botilleria.vista.voucher import RegistroVoucher


class Aplicacion(tk.Tk):
    def __init__(self, controlador: Controlador):
        super().__init__()
        self.controlador = controlador
        self.title("Botillería — Ventas")
        self.geometry("1100x700")
        self.minsize(940, 580)
        self._texto = elegir_fuente(self, FUENTES_TEXTO, "Helvetica")
        self._titulo = elegir_fuente(self, FUENTES_TITULO, "Times")
        self._aplicar_estilo()
        self._crear_menu()
        cuerpo = tk.Frame(self, background=PAPEL)
        cuerpo.pack(fill="both", expand=True)
        self._crear_panel_lateral(cuerpo)
        self._contenido = ttk.Frame(cuerpo)
        self._contenido.pack(side="left", fill="both", expand=True)
        self._pantallas = {
            "inicio": Inicio(self._contenido, controlador, self.mostrar),
            "productos": Productos(self._contenido, controlador),
            "clientes": Clientes(self._contenido, controlador),
            "pedidos": Pedidos(self._contenido, controlador),
            "detalle": Detalle(self._contenido, controlador),
            "pagos": Pagos(self._contenido, controlador),
            "voucher": RegistroVoucher(self._contenido, controlador),
        }
        self._actual = None
        self.mostrar("inicio")

    def _crear_panel_lateral(self, cuerpo: tk.Misc) -> None:
        """Panel negro con enlaces verde claro, en vez de botones."""
        panel = tk.Frame(cuerpo, background=NEGRO, width=220)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)
        tk.Label(
            panel,
            text="BOTILLERÍA",
            background=NEGRO,
            foreground="#FFFFFF",
            font=(self._titulo, 18, "bold"),
            anchor="center",
            justify="center",
        ).pack(fill="x", padx=8, pady=(28, 22))
        self._fuente_enlace = tkfont.Font(family=self._texto, size=11)
        self._fuente_activo = tkfont.Font(family=self._texto, size=11, weight="bold")
        self._fuente_hover = tkfont.Font(family=self._texto, size=11, underline=True)
        self._enlaces: dict[str, tk.Label] = {}
        self._clave_actual: str | None = None
        for clave, etiqueta in MODULOS:
            enlace = tk.Label(
                panel,
                text=etiqueta,
                background=NEGRO,
                foreground=ENLACE,
                font=self._fuente_enlace,
                anchor="w",
                cursor="hand2",
            )
            enlace.pack(fill="x", padx=8, ipadx=8, ipady=6, pady=1)
            enlace.bind("<Button-1>", lambda _evento, destino=clave: self.mostrar(destino))
            enlace.bind("<Enter>", lambda _evento, destino=clave: self._pasar_sobre(destino, True))
            enlace.bind("<Leave>", lambda _evento, destino=clave: self._pasar_sobre(destino, False))
            self._enlaces[clave] = enlace

    def _pasar_sobre(self, clave: str, dentro: bool) -> None:
        enlace = self._enlaces[clave]
        if clave == self._clave_actual:
            return
        enlace.configure(
            background=ACTIVO if dentro else NEGRO,
            font=self._fuente_hover if dentro else self._fuente_enlace,
        )

    def _aplicar_estilo(self) -> None:
        self.configure(background=PAPEL)
        for nombre in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(nombre).configure(family=self._texto, size=11)
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure(".", background=PAPEL, foreground=TINTA, font=(self._texto, 11))
        for nombre in ("TFrame", "TLabel", "TCheckbutton"):
            estilo.configure(nombre, background=PAPEL)
        estilo.configure("Titulo.TLabel", font=(self._titulo, 26, "bold"), background=PAPEL)
        estilo.configure(
            "Rotulo.TLabel", font=(self._texto, 10, "bold"), foreground=VERDE_TEXTO, background=PAPEL
        )
        estilo.configure("TNotebook", background=PAPEL, bordercolor=LINEA, tabmargins=(0, 0, 0, 0))
        estilo.configure(
            "TNotebook.Tab", background="#EFEADB", foreground=TINTA, padding=(16, 8),
            bordercolor=LINEA, font=(self._texto, 10, "bold"),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", CAMPO)],
            foreground=[("selected", VERDE_TEXTO)],
        )
        estilo.configure("Destacado.TLabel", font=(self._titulo, 15, "bold"), background=PAPEL)
        estilo.configure("TLabelframe", background=PAPEL, bordercolor=LINEA, lightcolor=PAPEL, darkcolor=PAPEL)
        estilo.configure(
            "TLabelframe.Label", background=PAPEL, foreground=VERDE_TEXTO, font=(self._texto, 10, "bold")
        )
        estilo.configure(
            "TButton", padding=(14, 6), background=CAMPO, foreground=TINTA,
            bordercolor=TINTA, lightcolor=CAMPO, darkcolor=CAMPO, focuscolor=CAMPO,
        )
        estilo.map(
            "TButton",
            background=[("disabled", "#EEEAE0"), ("active", "#EDE8D8")],
            foreground=[("disabled", "#8A8A80")],
            bordercolor=[("disabled", LINEA)],
        )
        estilo.configure(
            "Primario.TButton", padding=(14, 6), background=VERDE, foreground="#FFFFFF",
            bordercolor=VERDE, lightcolor=VERDE, darkcolor=VERDE, focuscolor=VERDE,
        )
        estilo.map(
            "Primario.TButton",
            background=[("disabled", "#9DB5A6"), ("active", "#0F3F22")],
            foreground=[("disabled", "#FFFFFF")],
            bordercolor=[("disabled", "#9DB5A6")],
        )
        estilo.configure(
            "TEntry", fieldbackground=CAMPO, bordercolor="#8A8A80", lightcolor=CAMPO, darkcolor=CAMPO, padding=4
        )
        estilo.configure(
            "TCombobox", fieldbackground=CAMPO, background=CAMPO, bordercolor="#8A8A80",
            lightcolor=CAMPO, darkcolor=CAMPO, arrowcolor=TINTA, padding=4,
        )
        estilo.map("TCombobox", fieldbackground=[("readonly", CAMPO)], foreground=[("readonly", TINTA)])
        estilo.configure(
            "Treeview", background=CAMPO, fieldbackground=CAMPO, foreground=TINTA,
            rowheight=28, bordercolor=LINEA, lightcolor=CAMPO, darkcolor=CAMPO,
        )
        estilo.map("Treeview", background=[("selected", SELECCION)], foreground=[("selected", TINTA)])
        estilo.configure(
            "Treeview.Heading", background="#EFEADB", foreground=TINTA,
            font=(self._texto, 9, "bold"), relief="flat", bordercolor=LINEA, padding=(6, 6),
        )
        estilo.configure("TScrollbar", background=LINEA, troughcolor=PAPEL, bordercolor=PAPEL, arrowcolor=GRIS)

    def _crear_menu(self) -> None:
        barra = tk.Menu(self)
        archivo = tk.Menu(barra, tearoff=0)
        archivo.add_command(label="Salir", command=self.destroy)
        barra.add_cascade(label="Archivo", menu=archivo)
        modulos = tk.Menu(barra, tearoff=0)
        for clave, etiqueta in MODULOS:
            modulos.add_command(label=etiqueta, command=lambda destino=clave: self.mostrar(destino))
        barra.add_cascade(label="Módulos", menu=modulos)
        self.configure(menu=barra)

    def mostrar(self, nombre: str) -> None:
        if self._actual is not None:
            self._actual.pack_forget()
        pantalla = self._pantallas[nombre]
        pantalla.refrescar()
        pantalla.pack(fill="both", expand=True)
        self._actual = pantalla
        self._clave_actual = nombre
        for clave, enlace in self._enlaces.items():
            activo = clave == nombre
            enlace.configure(
                background=ACTIVO if activo else NEGRO,
                font=self._fuente_activo if activo else self._fuente_enlace,
            )


def iniciar(directorio=None) -> None:
    """Carga los CSV y abre la ventana; si un archivo falla, avisa y termina."""
    try:
        controlador = crear_controlador(directorio)
    except PersistenciaError as error:
        raiz = tk.Tk()
        raiz.withdraw()
        mostrar_error(raiz, str(error))
        raiz.destroy()
        return
    Aplicacion(controlador).mainloop()
