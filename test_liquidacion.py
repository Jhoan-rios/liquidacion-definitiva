"""
Pruebas unitarias para el módulo logica_liquidacion.

Ejecutar con:
    python -m unittest test_liquidacion.py -v
o simplemente:
    python test_liquidacion.py
"""

import unittest
from datetime import datetime

from logica_liquidacion import (
    calcular_dias,
    calcular_salario_restante,
    calcular_prima,
    calcular_cesantias,
    calcular_intereses,
    calcular_vacaciones,
    calcular_indemnizacion,
    calcular_liquidacion,
    SalarioInvalidoException,
    FechaInvalidaException,
    TipoRetiroInvalidoException,
)


class LiquidacionTest(unittest.TestCase):

    def test_prima_para_180_dias(self):
        salario = 2_000_000
        dias = 180

        resultado = calcular_prima(
            salario,
            dias
        )

        esperado = 1_000_000

        self.assertEqual(
            esperado,
            resultado
        )

    def test_cesantias_para_360_dias(self):
        salario = 1_500_000
        dias = 360

        resultado = calcular_cesantias(
            salario,
            dias
        )

        esperado = 1_500_000

        self.assertEqual(
            esperado,
            resultado
        )

    def test_intereses_para_360_dias(self):
        cesantias = 1_200_000
        dias = 360

        resultado = calcular_intereses(
            cesantias,
            dias
        )

        esperado = 144_000

        self.assertEqual(
            esperado,
            resultado
        )

    def test_salario_restante(self):
        salario = 1_750_000

        fecha_retiro = datetime(
            2026,
            5,
            20
        )

        resultado = calcular_salario_restante(
            salario,
            fecha_retiro
        )

        esperado = (
            1_750_000 / 30
        ) * 20

        self.assertEqual(
            esperado,
            resultado
        )

    def test_vacaciones_con_5_dias_disfrutados(self):
        salario = 1_800_000
        dias = 360
        vacaciones_disfrutadas = 5

        resultado = calcular_vacaciones(
            salario,
            dias,
            vacaciones_disfrutadas
        )

        esperado = 600_000

        self.assertEqual(
            esperado,
            resultado
        )

    def test_vacaciones_no_pueden_ser_negativas(self):
        salario = 1_800_000
        dias = 360
        vacaciones_disfrutadas = 100

        resultado = calcular_vacaciones(
            salario,
            dias,
            vacaciones_disfrutadas
        )

        esperado = 0

        self.assertEqual(
            esperado,
            resultado
        )

    def test_indemnizacion_para_360_dias(self):
        salario = 1_800_000
        dias = 360

        resultado = calcular_indemnizacion(
            salario,
            dias
        )

        esperado = 1_800_000

        self.assertEqual(
            esperado,
            resultado
        )

    def test_calcular_dias(self):
        ingreso = datetime(
            2025,
            1,
            1
        )

        retiro = datetime(
            2025,
            7,
            1
        )

        resultado = calcular_dias(
            ingreso,
            retiro
        )

        esperado = 181

        self.assertEqual(
            esperado,
            resultado
        )

    def test_liquidacion_por_renuncia(self):
        salario = 2_000_000

        ingreso = datetime(
            2025,
            1,
            1
        )

        retiro = datetime(
            2025,
            12,
            27
        )

        resultado = calcular_liquidacion(
            "Renuncia",
            salario,
            ingreso,
            retiro,
            0
        )

        self.assertGreater(
            resultado,
            0
        )

    def test_salario_negativo_genera_error(self):

        with self.assertRaises(
            SalarioInvalidoException
        ):
            calcular_prima(
                -1_000_000,
                180
            )

    def test_salario_cero_genera_error(self):

        with self.assertRaises(
            SalarioInvalidoException
        ):
            calcular_prima(
                0,
                180
            )

    def test_fecha_invalida_genera_error(self):
        ingreso = datetime(
            2025,
            5,
            10
        )

        retiro = datetime(
            2025,
            2,
            10
        )

        with self.assertRaises(
            FechaInvalidaException
        ):
            calcular_dias(
                ingreso,
                retiro
            )

    def test_tipo_retiro_invalido_genera_error(self):
        ingreso = datetime(
            2025,
            1,
            1
        )

        retiro = datetime(
            2025,
            12,
            1
        )

        with self.assertRaises(
            TipoRetiroInvalidoException
        ):
            calcular_liquidacion(
                "Vacaciones",
                2_000_000,
                ingreso,
                retiro,
                0
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )