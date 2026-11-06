"""Punto de entrada compatible con `python main.py` desde la raíz del proyecto."""
from pathlib import Path
import sys


RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    """Inicia la interfaz gráfica de Botillería."""
    from botilleria.__main__ import main as iniciar

    iniciar()


if __name__ == "__main__":
    main()
