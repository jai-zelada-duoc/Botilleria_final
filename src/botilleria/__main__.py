"""Punto de entrada: `python -m botilleria` abre la aplicación de escritorio."""


def main() -> None:
    """Inicia la interfaz y da instrucciones claras si falta Tkinter."""
    try:
        from botilleria.vista.aplicacion import iniciar
    except ModuleNotFoundError as error:
        if error.name not in {"tkinter", "tkinter.font"}:
            raise
        raise SystemExit(
            "No está disponible Tkinter, necesario para abrir la ventana de Botillería.\n"
            "En Ubuntu/Debian instala el paquete con: sudo apt install python3-tk\n"
            "En Windows, modifica la instalación de Python y agrega 'tcl/tk and IDLE'.\n"
            "En macOS, usa una instalación de Python que incluya Tkinter."
        ) from error
    iniciar()


if __name__ == "__main__":
    main()
