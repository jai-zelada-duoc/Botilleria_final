"""Pruebas de regresión para la carga CSV y el ciclo de una venta."""
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from botilleria.controladores import crear_controlador
from botilleria.modelo.errores import PersistenciaError
from botilleria.persistencia import RepositorioCSV


CLIENTES_OK = (
    "id,nombre,telefono,direccion,es_vip,compras,total_comprado\n"
    "C001,Cliente Ejemplo,+56912345678,Calle 1,no,0,0\n"
)
PRODUCTOS_OK = (
    "id,tipo,nombre,precio,stock,mililitros,categoria\n"
    "P001,bebida,Bebida de prueba,1000,5,350,\n"
)


class PersistenciaCSVTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.directorio = Path(self.temporal.name)
        (self.directorio / "clientes.csv").write_text(CLIENTES_OK, encoding="utf-8")
        (self.directorio / "productos.csv").write_text(PRODUCTOS_OK, encoding="utf-8")
        self.repositorio = RepositorioCSV(self.directorio)

    def tearDown(self):
        self.temporal.cleanup()

    def test_rechaza_identificadores_duplicados_en_productos(self):
        (self.directorio / "productos.csv").write_text(
            PRODUCTOS_OK + "P001,snack,Otro,500,2,,Salado\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(PersistenciaError, "fila 3.*identificador repetido"):
            self.repositorio.cargar_productos()

    def test_rechaza_identificadores_duplicados_en_clientes(self):
        (self.directorio / "clientes.csv").write_text(
            CLIENTES_OK + "C001,Otro Cliente,+56912345679,Calle 2,si,0,0\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(PersistenciaError, "fila 3.*identificador repetido"):
            self.repositorio.cargar_clientes()

    def test_rechaza_campos_sobrantes_en_fila_csv(self):
        (self.directorio / "productos.csv").write_text(
            PRODUCTOS_OK + "P002,snack,Extra,500,2,,Salado,inesperado\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(PersistenciaError, "fila 3.*más valores que columnas"):
            self.repositorio.cargar_productos()

    def test_pagar_y_cancelar_actualiza_y_restituye_stock(self):
        controlador = crear_controlador(self.directorio, guardar=False)
        cliente = controlador.listar_clientes()[0]
        pedido = controlador.crear_pedido(cliente.id)
        controlador.agregar_producto(pedido.id, "P001", "2")

        resultado = controlador.pagar(pedido.id, "Tarjeta", False, "", "")
        self.assertTrue(resultado.aprobado)
        self.assertEqual(controlador.obtener_producto("P001").stock, 3)

        controlador.cancelar(pedido.id)
        self.assertEqual(controlador.obtener_producto("P001").stock, 5)
        self.assertTrue(pedido.stock_restituido)


if __name__ == "__main__":
    unittest.main()
