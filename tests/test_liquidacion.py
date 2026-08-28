"""
Pruebas unitarias para la lógica de liquidación laboral.
"""

import unittest
from datetime import datetime

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


class TestLiquidacion(unittest.TestCase):
    """Pruebas de la lógica de liquidación."""

    def test_calcular_dias_trabajados(self):
        fecha_ingreso = datetime(2025, 1, 1)
        fecha_retiro = datetime(2025, 7, 1)

        resultado = calcular_dias_trabajados(
            fecha_ingreso,
            fecha_retiro,
        )

        self.assertEqual(resultado, 181)

    def test_calcular_dias_trabajados_fecha_invalida(self):
        fecha_ingreso = datetime(2025, 7, 1)
        fecha_retiro = datetime(2025, 1, 1)

        with self.assertRaises(FechaInvalidaError):
            calcular_dias_trabajados(
                fecha_ingreso,
                fecha_retiro,
            )

    def test_calcular_salario_restante(self):
        resultado = calcular_salario_restante(
            3_000_000,
            datetime(2025, 6, 15),
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
            360,
        )

        self.assertEqual(resultado, 3_000_000)

    def test_calcular_proporcion_anual(self):
        resultado = calcular_proporcion_anual(
            3_000_000,
            180,
        )

        self.assertEqual(resultado, 1_500_000)

    def test_calcular_intereses(self):
        resultado = calcular_intereses(
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 360_000)

    def test_calcular_vacaciones_generadas(self):
        resultado = calcular_vacaciones_generadas(
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 1_500_000)

    def test_calcular_valor_vacaciones_disfrutadas(self):
        resultado = calcular_valor_vacaciones_disfrutadas(
            3_000_000,
            10,
        )

        self.assertEqual(resultado, 1_000_000)

    def test_calcular_vacaciones(self):
        resultado = calcular_vacaciones(
            3_000_000,
            360,
            10,
        )

        self.assertEqual(resultado, 500_000)

    def test_calcular_vacaciones_no_negativas(self):
        resultado = calcular_vacaciones(
            3_000_000,
            360,
            30,
        )

        self.assertEqual(resultado, 0)

    def test_calcular_indemnizacion(self):
        resultado = calcular_indemnizacion(
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 3_000_000)

    def test_calcular_dias_indemnizacion_un_ano(self):
        resultado = calcular_dias_indemnizacion(360)

        self.assertEqual(resultado, 30)

    def test_calcular_dias_indemnizacion_dos_anos(self):
        resultado = calcular_dias_indemnizacion(720)

        self.assertEqual(resultado, 50)

    def test_calcular_indemnizacion_por_renuncia(self):
        resultado = calcular_indemnizacion_por_tipo_retiro(
            RENUNCIA,
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 0)

    def test_calcular_indemnizacion_por_justa_causa(self):
        resultado = calcular_indemnizacion_por_tipo_retiro(
            DESPIDO_CON_JUSTA_CAUSA,
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 0)

    def test_calcular_indemnizacion_por_sin_justa_causa(self):
        resultado = calcular_indemnizacion_por_tipo_retiro(
            DESPIDO_SIN_JUSTA_CAUSA,
            3_000_000,
            360,
        )

        self.assertEqual(resultado, 3_000_000)

    def test_tipo_retiro_invalido(self):
        with self.assertRaises(TipoRetiroInvalidoError):
            calcular_indemnizacion_por_tipo_retiro(
                "Vacaciones",
                3_000_000,
                360,
            )

    def test_salario_negativo(self):
        with self.assertRaises(SalarioInvalidoError):
            calcular_prima(
                -1_000_000,
                180,
            )

    def test_salario_cero(self):
        with self.assertRaises(SalarioInvalidoError):
            calcular_prima(
                0,
                180,
            )

    def test_vacaciones_negativas(self):
        with self.assertRaises(VacacionesInvalidasError):
            calcular_vacaciones(
                3_000_000,
                360,
                -1,
            )

    def test_sumar_conceptos_liquidacion(self):
        conceptos = ConceptosLiquidacion(
            salario_restante=1_000_000,
            prima=500_000,
            cesantias=500_000,
            intereses=60_000,
            vacaciones=250_000,
            indemnizacion=0,
        )

        resultado = sumar_conceptos_liquidacion(conceptos)

        self.assertEqual(resultado, 2_310_000)

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


if __name__ == "__main__":
    unittest.main()