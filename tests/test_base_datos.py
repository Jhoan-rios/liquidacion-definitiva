"""
Pruebas de la integración con PostgreSQL (crear/borrar tablas,
insertar y buscar liquidaciones).

Usan la base de datos DB_NAME_TEST de secret_config.py. Por seguridad
su nombre debe terminar en "_test", porque cada prueba borra y crea
las tablas.
"""

import sys
import unittest
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


from controller.liquidacion_controller import LiquidacionController
from model.base_datos import (
    cargar_configuracion_secreta,
    construir_url,
    crear_engine,
)
from model.excepciones import (
    DocumentoInvalidoError,
    EmpleadoNoEncontradoError,
    ErrorConexionBDError,
    FechaInvalidaError,
    LiquidacionNoEncontradaError,
    NombreInvalidoError,
    SalarioInvalidoError,
    TablasNoCreadasError,
    TipoRetiroInvalidoError,
)
from model.logica_liquidacion import (
    DESPIDO_SIN_JUSTA_CAUSA,
    RENUNCIA,
    DatosLiquidacion,
    calcular_liquidacion,
)


DOCUMENTO = "1020304050"
NOMBRE = "Jhoan Ríos"


def crear_datos(
    tipo_retiro: str = DESPIDO_SIN_JUSTA_CAUSA,
    salario: float = 3_000_000,
    vacaciones_disfrutadas: int = 0,
    fecha_retiro: datetime = datetime(2025, 12, 31),
) -> DatosLiquidacion:
    """Crea datos de liquidación válidos para las pruebas."""

    return DatosLiquidacion(
        tipo_retiro=tipo_retiro,
        salario=salario,
        fecha_ingreso=datetime(2025, 1, 1),
        fecha_retiro=fecha_retiro,
        vacaciones_disfrutadas=vacaciones_disfrutadas,
    )


class BaseDatosTestCase(unittest.TestCase):
    """Fixtures: dejan la BD de pruebas con las tablas vacías."""

    @classmethod
    def setUpClass(cls):
        config = cargar_configuracion_secreta()

        if not config.DB_NAME_TEST.endswith("_test"):
            raise RuntimeError(
                "DB_NAME_TEST debe terminar en '_test' porque las "
                "pruebas borran las tablas."
            )

        cls.engine = crear_engine(construir_url(config.DB_NAME_TEST))
        cls.controlador = LiquidacionController(cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.controlador.borrar_tablas()
        self.controlador.crear_tablas()

    def tearDown(self):
        self.controlador.borrar_tablas()

    def nombres_de_tablas(self) -> set[str]:
        """Consulta a PostgreSQL qué tablas existen."""

        return set(inspect(self.engine).get_table_names())


class TestCrearTablas(BaseDatosTestCase):

    def test_crear_tablas_crea_empleados_y_liquidaciones(self):
        self.assertEqual(
            self.nombres_de_tablas(),
            {"empleados", "liquidaciones"},
        )

    def test_crear_tablas_dos_veces_no_falla(self):
        self.controlador.crear_tablas()

        self.assertEqual(
            self.nombres_de_tablas(),
            {"empleados", "liquidaciones"},
        )


class TestBorrarTablas(BaseDatosTestCase):

    def test_borrar_tablas_elimina_todo(self):
        self.controlador.borrar_tablas()

        self.assertEqual(self.nombres_de_tablas(), set())

    def test_borrar_tablas_elimina_tambien_los_datos(self):
        self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )

        self.controlador.borrar_tablas()
        self.controlador.crear_tablas()

        with self.assertRaises(EmpleadoNoEncontradoError):
            self.controlador.buscar_por_documento(DOCUMENTO)


class TestInsertar(BaseDatosTestCase):

    def test_insertar_guarda_la_liquidacion_con_su_total(self):
        datos = crear_datos()

        guardada = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, datos
        )

        self.assertIsNotNone(guardada["id"])
        self.assertEqual(guardada["documento"], DOCUMENTO)
        self.assertEqual(guardada["nombre"], NOMBRE)
        self.assertEqual(guardada["fecha_retiro"], date(2025, 12, 31))
        self.assertAlmostEqual(
            guardada["total"],
            calcular_liquidacion(datos),
            places=2,
        )

    def test_insertar_guarda_cada_concepto(self):
        guardada = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )

        suma = (
            guardada["salario_restante"]
            + guardada["prima"]
            + guardada["cesantias"]
            + guardada["intereses"]
            + guardada["vacaciones"]
            + guardada["indemnizacion"]
        )

        self.assertAlmostEqual(suma, guardada["total"], delta=0.05)
        self.assertGreater(guardada["indemnizacion"], 0)

    def test_renuncia_se_guarda_sin_indemnizacion(self):
        guardada = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos(tipo_retiro=RENUNCIA)
        )

        self.assertEqual(guardada["indemnizacion"], 0)

    def test_mismo_documento_reutiliza_al_empleado(self):
        self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )
        self.controlador.registrar_liquidacion(
            DOCUMENTO, "Otro Nombre", crear_datos(salario=4_000_000)
        )

        liquidaciones = self.controlador.buscar_por_documento(DOCUMENTO)

        self.assertEqual(len(liquidaciones), 2)
        self.assertEqual(liquidaciones[1]["nombre"], NOMBRE)

    def test_insertar_con_salario_invalido_no_guarda_nada(self):
        with self.assertRaises(SalarioInvalidoError):
            self.controlador.registrar_liquidacion(
                DOCUMENTO, NOMBRE, crear_datos(salario=0)
            )

        with self.assertRaises(EmpleadoNoEncontradoError):
            self.controlador.buscar_por_documento(DOCUMENTO)

    def test_insertar_con_fecha_retiro_anterior_falla(self):
        with self.assertRaises(FechaInvalidaError):
            self.controlador.registrar_liquidacion(
                DOCUMENTO,
                NOMBRE,
                crear_datos(fecha_retiro=datetime(2024, 1, 1)),
            )

    def test_insertar_con_documento_vacio_falla(self):
        with self.assertRaises(DocumentoInvalidoError):
            self.controlador.registrar_liquidacion(
                "  ", NOMBRE, crear_datos()
            )

    def test_insertar_con_documento_con_simbolos_falla(self):
        with self.assertRaises(DocumentoInvalidoError):
            self.controlador.registrar_liquidacion(
                "123'; DROP TABLE empleados;--", NOMBRE, crear_datos()
            )

    def test_insertar_con_nombre_vacio_falla(self):
        with self.assertRaises(NombreInvalidoError):
            self.controlador.registrar_liquidacion(
                DOCUMENTO, "", crear_datos()
            )


class TestBuscar(BaseDatosTestCase):

    def test_buscar_por_documento_devuelve_sus_liquidaciones(self):
        self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )
        self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos(tipo_retiro=RENUNCIA)
        )
        self.controlador.registrar_liquidacion(
            "999888777", "Andrés Rosas", crear_datos()
        )

        liquidaciones = self.controlador.buscar_por_documento(DOCUMENTO)

        self.assertEqual(len(liquidaciones), 2)
        self.assertEqual(
            [liq["tipo_retiro"] for liq in liquidaciones],
            [DESPIDO_SIN_JUSTA_CAUSA, RENUNCIA],
        )

    def test_buscar_por_id_devuelve_la_liquidacion(self):
        guardada = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )

        encontrada = self.controlador.buscar_por_id(guardada["id"])

        self.assertEqual(encontrada["id"], guardada["id"])
        self.assertEqual(encontrada["nombre"], NOMBRE)
        self.assertEqual(encontrada["total"], guardada["total"])

    def test_buscar_documento_inexistente_falla(self):
        with self.assertRaises(EmpleadoNoEncontradoError):
            self.controlador.buscar_por_documento("55555555")

    def test_buscar_documento_invalido_falla(self):
        with self.assertRaises(DocumentoInvalidoError):
            self.controlador.buscar_por_documento("")

    def test_buscar_id_inexistente_falla(self):
        with self.assertRaises(LiquidacionNoEncontradaError):
            self.controlador.buscar_por_id(987654)


class TestFuncionalidadesAdicionales(BaseDatosTestCase):

    def registrar_dos_empleados(self):
        self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )
        self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos(tipo_retiro=RENUNCIA)
        )
        self.controlador.registrar_liquidacion(
            "999888777", "Andrés Rosas", crear_datos()
        )

    def test_listar_liquidaciones_mas_reciente_primero(self):
        self.registrar_dos_empleados()

        todas = self.controlador.listar_liquidaciones()

        self.assertEqual(len(todas), 3)
        self.assertGreater(todas[0]["id"], todas[-1]["id"])
        self.assertEqual(len(self.controlador.listar_liquidaciones(limite=2)), 2)

    def test_listar_liquidaciones_sin_datos_devuelve_lista_vacia(self):
        self.assertEqual(self.controlador.listar_liquidaciones(), [])

    def test_buscar_por_tipo_retiro(self):
        self.registrar_dos_empleados()

        renuncias = self.controlador.buscar_por_tipo_retiro(RENUNCIA)

        self.assertEqual(len(renuncias), 1)
        self.assertEqual(renuncias[0]["tipo_retiro"], RENUNCIA)

    def test_buscar_por_tipo_retiro_invalido_falla(self):
        with self.assertRaises(TipoRetiroInvalidoError):
            self.controlador.buscar_por_tipo_retiro("Inventado")

    def test_listar_empleados_con_cantidad_de_liquidaciones(self):
        self.registrar_dos_empleados()

        empleados = self.controlador.listar_empleados()

        self.assertEqual(
            [(e["documento"], e["cantidad_liquidaciones"]) for e in empleados],
            [(DOCUMENTO, 2), ("999888777", 1)],
        )

    def test_obtener_total_liquidado_suma_las_liquidaciones(self):
        primera = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )
        segunda = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos(tipo_retiro=RENUNCIA)
        )

        total = self.controlador.obtener_total_liquidado(DOCUMENTO)

        self.assertAlmostEqual(
            total, primera["total"] + segunda["total"], places=2
        )

    def test_obtener_total_empleado_inexistente_falla(self):
        with self.assertRaises(EmpleadoNoEncontradoError):
            self.controlador.obtener_total_liquidado("123")

    def test_actualizar_nombre_empleado(self):
        self.registrar_dos_empleados()

        self.controlador.actualizar_nombre_empleado(DOCUMENTO, "Nuevo Nombre")

        liquidaciones = self.controlador.buscar_por_documento(DOCUMENTO)
        self.assertEqual(liquidaciones[0]["nombre"], "Nuevo Nombre")

    def test_actualizar_nombre_invalido_o_inexistente_falla(self):
        self.registrar_dos_empleados()

        with self.assertRaises(NombreInvalidoError):
            self.controlador.actualizar_nombre_empleado(DOCUMENTO, "  ")

        with self.assertRaises(EmpleadoNoEncontradoError):
            self.controlador.actualizar_nombre_empleado("123", "Alguien")

    def test_eliminar_liquidacion(self):
        guardada = self.controlador.registrar_liquidacion(
            DOCUMENTO, NOMBRE, crear_datos()
        )

        self.controlador.eliminar_liquidacion(guardada["id"])

        with self.assertRaises(LiquidacionNoEncontradaError):
            self.controlador.buscar_por_id(guardada["id"])

    def test_eliminar_liquidacion_inexistente_falla(self):
        with self.assertRaises(LiquidacionNoEncontradaError):
            self.controlador.eliminar_liquidacion(424242)

    def test_eliminar_empleado_borra_sus_liquidaciones(self):
        self.registrar_dos_empleados()

        borradas = self.controlador.eliminar_empleado(DOCUMENTO)

        self.assertEqual(borradas, 2)
        self.assertEqual(len(self.controlador.listar_liquidaciones()), 1)

        with self.assertRaises(EmpleadoNoEncontradoError):
            self.controlador.eliminar_empleado(DOCUMENTO)

    def test_funcionalidades_sin_conexion_o_sin_tablas(self):
        self.controlador.borrar_tablas()

        with self.assertRaises(TablasNoCreadasError):
            self.controlador.listar_liquidaciones()

        with self.assertRaises(TablasNoCreadasError):
            self.controlador.listar_empleados()


class TestSinTablas(BaseDatosTestCase):
    """Usar la BD sin haber creado las tablas da un error claro."""

    def setUp(self):
        self.controlador.borrar_tablas()

    def test_insertar_sin_tablas_falla(self):
        with self.assertRaises(TablasNoCreadasError):
            self.controlador.registrar_liquidacion(
                DOCUMENTO, NOMBRE, crear_datos()
            )

    def test_buscar_sin_tablas_falla(self):
        with self.assertRaises(TablasNoCreadasError):
            self.controlador.buscar_por_documento(DOCUMENTO)

        with self.assertRaises(TablasNoCreadasError):
            self.controlador.buscar_por_id(1)


class TestErroresDeConexion(unittest.TestCase):
    """Cada funcionalidad debe avisar si la BD no está disponible."""

    @classmethod
    def setUpClass(cls):
        url_inalcanzable = URL.create(
            drivername="postgresql+psycopg2",
            username="nadie",
            password="nada",
            host="127.0.0.1",
            port=1,
            database="no_existe",
        )

        cls.controlador = LiquidacionController(
            crear_engine(url_inalcanzable)
        )

    def test_crear_tablas_sin_conexion(self):
        with self.assertRaises(ErrorConexionBDError):
            self.controlador.crear_tablas()

    def test_borrar_tablas_sin_conexion(self):
        with self.assertRaises(ErrorConexionBDError):
            self.controlador.borrar_tablas()

    def test_insertar_sin_conexion(self):
        with self.assertRaises(ErrorConexionBDError):
            self.controlador.registrar_liquidacion(
                DOCUMENTO, NOMBRE, crear_datos()
            )

    def test_buscar_sin_conexion(self):
        with self.assertRaises(ErrorConexionBDError):
            self.controlador.buscar_por_documento(DOCUMENTO)


if __name__ == "__main__":
    unittest.main()
