"""
Pruebas unitarias para la lógica de liquidación laboral.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


from model.logica_liquidacion import (
    RENUNCIA,
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
    ConceptosLiquidacion,
    DatosLiquidacion,
    calcular_dias_trabajados,
    calcular_salario_restante,
    calcular_prima,
    calcular_cesantias,
    calcular_proporcion_anual,
    calcular_intereses,
    calcular_vacaciones,
    calcular_vacaciones_generadas,
    calcular_valor_vacaciones_disfrutadas,
    calcular_indemnizacion,
    calcular_dias_indemnizacion,
    calcular_indemnizacion_por_tipo_retiro,
    calcular_liquidacion,
    sumar_conceptos_liquidacion,
)

from model.excepciones import (
    FechaInvalidaError,
    SalarioInvalidoError,
    TipoRetiroInvalidoError,
    VacacionesInvalidasError,
)


class TestLogicaLiquidacion(unittest.TestCase):

    def setUp(self):
        self.salario = 3_000_000
        self.fecha_ingreso = datetime(2025, 1, 1)
        self.fecha_retiro = datetime(2025, 12, 31)

    def test_salario_invalido(self):
        with self.assertRaises(SalarioInvalidoError):
            calcular_salario_restante(
                0,
                self.fecha_retiro,
            )

    def test_salario_negativo(self):
        with self.assertRaises(SalarioInvalidoError):
            calcular_prima(
                -1000,
                100,
            )

    def test_calcular_dias_trabajados(self):
        dias = calcular_dias_trabajados(
            datetime(2025, 1, 1),
            datetime(2025, 1, 31),
        )

        self.assertEqual(dias, 30)

    def test_fecha_retiro_anterior(self):
        with self.assertRaises(FechaInvalidaError):
            calcular_dias_trabajados(
                datetime(2025, 5, 1),
                datetime(2025, 4, 1),
            )

    def test_calcular_salario_restante(self):
        resultado = calcular_salario_restante(
            3_000_000,
            datetime(2025, 1, 15),
        )

        self.assertEqual(resultado, 1_500_000)

    def test_calcular_proporcion_anual(self):
        resultado = calcular_proporcion_anual(
            3_000_000,
            180,
        )

        self.assertEqual(resultado, 1_500_000)

    def test_calcular_prima(self):
        resultado = calcular_prima(
            3_000_000,
            180,
        )

        self.assertEqual(resultado, 1_500_000)

    def test_calcular_cesantias(self):
        resultado = calcular_cesantias(
            3_000_000,
            180,
        )

        self.assertEqual(resultado, 1_500_000)

    def test_calcular_intereses(self):
        cesantias = 1_500_000

        resultado = calcular_intereses(
            cesantias,
            180,
        )

        self.assertEqual(resultado, 90_000)

    def test_calcular_vacaciones_generadas(self):
        resultado = calcular_vacaciones_generadas(
            3_000_000,
            180,
        )

        self.assertEqual(resultado, 750_000)

    def test_calcular_valor_vacaciones_disfrutadas(self):
        resultado = calcular_valor_vacaciones_disfrutadas(
            3_000_000,
            5,
        )

        self.assertEqual(resultado, 500_000)

    def test_calcular_vacaciones(self):
        resultado = calcular_vacaciones(
            3_000_000,
            180,
            5,
        )

        self.assertEqual(resultado, 250_000)

    def test_vacaciones_negativas(self):
        with self.assertRaises(VacacionesInvalidasError):
            calcular_vacaciones(
                3_000_000,
                180,
                -1,
            )

    def test_calcular_dias_indemnizacion_hasta_un_ano(self):
        resultado = calcular_dias_indemnizacion(360)

        self.assertEqual(resultado, 30)

    def test_calcular_dias_indemnizacion_un_ano_y_medio(self):
        resultado = calcular_dias_indemnizacion(540)

        self.assertEqual(resultado, 40)

    def test_calcular_dias_indemnizacion_dos_anos(self):
        resultado = calcular_dias_indemnizacion(720)

        self.assertEqual(resultado, 50)

    def test_calcular_indemnizacion(self):
        resultado = calcular_indemnizacion(
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 3_000_000)

    def test_renuncia_no_genera_indemnizacion(self):
        resultado = calcular_indemnizacion_por_tipo_retiro(
            RENUNCIA,
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 0)

    def test_despido_con_justa_causa_no_genera_indemnizacion(self):
        resultado = calcular_indemnizacion_por_tipo_retiro(
            DESPIDO_CON_JUSTA_CAUSA,
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 0)

    def test_despido_sin_justa_causa_genera_indemnizacion(self):
        resultado = calcular_indemnizacion_por_tipo_retiro(
            DESPIDO_SIN_JUSTA_CAUSA,
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 3_000_000)

    def test_tipo_retiro_invalido(self):
        with self.assertRaises(TipoRetiroInvalidoError):
            calcular_indemnizacion_por_tipo_retiro(
                "Tipo inválido",
                3_000_000,
                360,
            )

    def test_sumar_conceptos_liquidacion(self):
        conceptos = ConceptosLiquidacion(
            salario_restante=100,
            prima=200,
            cesantias=300,
            intereses=400,
            vacaciones=500,
            indemnizacion=600,
        )

        resultado = sumar_conceptos_liquidacion(conceptos)

        self.assertEqual(resultado, 2100)

    def test_calcular_liquidacion_renuncia(self):
        datos = DatosLiquidacion(
            tipo_retiro=RENUNCIA,
            salario=3_000_000,
            fecha_ingreso=datetime(2025, 1, 1),
            fecha_retiro=datetime(2025, 12, 31),
            vacaciones_disfrutadas=0,
        )

        resultado = calcular_liquidacion(datos)

        self.assertGreater(resultado, 0)

    def test_calcular_liquidacion_despido_sin_justa_causa(self):
        datos = DatosLiquidacion(
            tipo_retiro=DESPIDO_SIN_JUSTA_CAUSA,
            salario=3_000_000,
            fecha_ingreso=datetime(2025, 1, 1),
            fecha_retiro=datetime(2025, 12, 31),
            vacaciones_disfrutadas=0,
        )

        resultado = calcular_liquidacion(datos)

        self.assertGreater(resultado, 0)


if __name__ == "__main__":
    unittest.main()