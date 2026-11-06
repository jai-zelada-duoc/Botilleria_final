"""Cliente que realiza un pedido."""

from botilleria.modelo.errores import ReglaNegocioError
from botilleria.modelo.validacion import booleano, exigir_entero, texto_obligatorio


class Cliente:
    def __init__(
        self,
        id: str,
        nombre: str,
        telefono: str,
        direccion: str,
        es_vip: bool,
        compras: int = 0,
        total_comprado: int = 0,
    ):
        self._id = texto_obligatorio(id, "Identificador")
        self._nombre = texto_obligatorio(nombre, "Nombre")
        self._telefono = texto_obligatorio(telefono, "Teléfono")
        if sum(caracter.isdigit() for caracter in self._telefono) < 8:
            raise ReglaNegocioError("El teléfono debe tener al menos 8 dígitos")
        self._direccion = texto_obligatorio(direccion, "Dirección")
        self._es_vip = booleano(es_vip, "El indicador VIP")
        self._compras = exigir_entero(compras, "Compras", minimo=0)
        self._total_comprado = exigir_entero(total_comprado, "Total comprado", minimo=0)

    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def direccion(self) -> str:
        return self._direccion

    @property
    def es_vip(self) -> bool:
        return self._es_vip

    @property
    def compras(self) -> int:
        return self._compras

    @property
    def total_comprado(self) -> int:
        return self._total_comprado

    def registrar_compra(self, monto: int) -> None:
        """Suma una compra pagada al historial del cliente."""
        monto_valido = exigir_entero(monto, "Monto", minimo=0)
        self._compras += 1
        self._total_comprado += monto_valido

    def anular_compra(self, monto: int) -> None:
        """Resta una compra que se canceló después de pagarse."""
        monto_valido = exigir_entero(monto, "Monto", minimo=0)
        self._compras = max(0, self._compras - 1)
        self._total_comprado = max(0, self._total_comprado - monto_valido)

    def actualizar(self, nombre: str, telefono: str, direccion: str, es_vip: bool) -> None:
        """Valida todo primero; si algo falla, el cliente no cambia."""
        nombre_limpio = texto_obligatorio(nombre, "Nombre")
        telefono_limpio = texto_obligatorio(telefono, "Teléfono")
        if sum(caracter.isdigit() for caracter in telefono_limpio) < 8:
            raise ReglaNegocioError("El teléfono debe tener al menos 8 dígitos")
        direccion_limpia = texto_obligatorio(direccion, "Dirección")
        vip = booleano(es_vip, "El indicador VIP")
        self._nombre = nombre_limpio
        self._telefono = telefono_limpio
        self._direccion = direccion_limpia
        self._es_vip = vip

    def a_diccionario(self) -> dict:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "telefono": self._telefono,
            "direccion": self._direccion,
            "es_vip": self._es_vip,
            "compras": self._compras,
            "total_comprado": self._total_comprado,
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Cliente":
        try:
            return cls(
                str(datos["id"]),
                datos["nombre"],
                datos["telefono"],
                datos["direccion"],
                datos["es_vip"],
                datos.get("compras", 0),
                datos.get("total_comprado", 0),
            )
        except (KeyError, TypeError) as error:
            raise ReglaNegocioError("Cliente guardado incompleto") from error

    def __repr__(self) -> str:
        return f"Cliente({self._nombre!r})"
