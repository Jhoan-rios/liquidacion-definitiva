import unittest
from datetime import datetime


# ==========================
# CONSTANTES
# ==========================

DIAS_ANO = 360
DIAS_MES = 30
PORCENTAJE_INTERESES = 0.12
DIAS_INDEMNIZACION_BASE = 30
DIAS_INDEMNIZACION_ADICIONALES = 20


# ==========================
# EXCEPCIONES
# ==========================

class SalarioInvalidoException(Exception):
    pass


class FechaInvalidaException(Exception):
    pass


class TipoRetiroInvalidoException(Exception):
    pass


# ==========================
# VALIDACIONES
# ==========================

def validar_salario(salario):
    if salario <= 0:
        raise SalarioInvalidoException(
            "El salario debe ser mayor que cero."
        )


# ==========================
# FUNCIONES
# ==========================

def calcular_dias(fecha_ingreso, fecha_retiro):
    if fecha_retiro < fecha_ingreso:
        raise FechaInvalidaException(
            "La fecha de retiro es inválida."
        )

    return (fecha_retiro - fecha_ingreso).days


def calcular_prima(salario, dias):
    validar_salario(salario)

    return (salario * dias) / DIAS_ANO


def calcular_cesantias(salario, dias):
    validar_salario(salario)

    return (salario * dias) / DIAS_ANO


def calcular_intereses(cesantias, dias):
    return (cesantias * PORCENTAJE_INTERESES * dias) / DIAS_ANO


def calcular_vacaciones(salario, dias, vacaciones_disfrutadas):
    validar_salario(salario)

    vacaciones_generadas = (salario * dias) / (DIAS_ANO * 2)

    descuento = (salario / DIAS_MES) * vacaciones_disfrutadas

    vacaciones_pendientes = vacaciones_generadas - descuento

    return max(vacaciones_pendientes, 0)


def calcular_indemnizacion(salario, dias):
    validar_salario(salario)

    salario_dia = salario / DIAS_MES

    dias_indemnizacion = DIAS_INDEMNIZACION_BASE

    if dias > DIAS_ANO:
        dias_restantes = dias - DIAS_ANO

        anos = dias_restantes // DIAS_ANO

        dias_indemnizacion += (
            anos * DIAS_INDEMNIZACION_ADICIONALES
        )

        fraccion = dias_restantes % DIAS_ANO

        dias_indemnizacion += (
            fraccion * DIAS_INDEMNIZACION_ADICIONALES
        ) / DIAS_ANO

    return salario_dia * dias_indemnizacion


def calcular_liquidacion(
    tipo_retiro,
    salario,
    fecha_ingreso,
    fecha_retiro,
    vacaciones_disfrutadas
):
    dias = calcular_dias(fecha_ingreso, fecha_retiro)

    prima = calcular_prima(salario, dias)

    cesantias = calcular_cesantias(salario, dias)

    intereses = calcular_intereses(cesantias, dias)

    vacaciones = calcular_vacaciones(
        salario,
        dias,
        vacaciones_disfrutadas
    )

    if tipo_retiro == "Renuncia":
        indemnizacion = 0

    elif tipo_retiro == "Despido con justa causa":
        indemnizacion = 0

    elif tipo_retiro == "Despido sin justa causa":
        indemnizacion = calcular_indemnizacion(
            salario,
            dias
        )

    else:
        raise TipoRetiroInvalidoException(
            "Tipo de retiro inválido."
        )

    return (
        prima
        + cesantias
        + intereses
        + vacaciones
        + indemnizacion
    )


# ==========================
# PRUEBAS UNITARIAS
# ==========================

class LiquidacionTest(unittest.TestCase):

    def test_prima_para_180_dias(self):
        salario = 2_000_000
        dias = 180

        resultado = calcular_prima(salario, dias)

        esperado = 1_000_000

        self.assertEqual(esperado, resultado)

    def test_cesantias_para_360_dias(self):
        salario = 1_500_000
        dias = 360

        resultado = calcular_cesantias(salario, dias)

        esperado = 1_500_000

        self.assertEqual(esperado, resultado)

    def test_intereses_para_360_dias(self):
        cesantias = 1_200_000
        dias = 360

        resultado = calcular_intereses(cesantias, dias)

        esperado = 144_000

        self.assertEqual(esperado, resultado)

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

        self.assertEqual(esperado, resultado)

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

        self.assertEqual(esperado, resultado)

    def test_indemnizacion_para_360_dias(self):
        salario = 1_800_000
        dias = 360

        resultado = calcular_indemnizacion(
            salario,
            dias
        )

        esperado = 1_800_000

        self.assertEqual(esperado, resultado)

    def test_calcular_dias(self):
        ingreso = datetime(2025, 1, 1)
        retiro = datetime(2025, 7, 1)

        resultado = calcular_dias(
            ingreso,
            retiro
        )

        esperado = 181

        self.assertEqual(esperado, resultado)

    def test_liquidacion_por_renuncia(self):
        salario = 2_000_000

        ingreso = datetime(2025, 1, 1)
        retiro = datetime(2025, 12, 27)

        resultado = calcular_liquidacion(
            "Renuncia",
            salario,
            ingreso,
            retiro,
            0
        )

        self.assertGreater(resultado, 0)

    def test_salario_negativo_genera_error(self):
        with self.assertRaises(SalarioInvalidoException):
            calcular_prima(-1_000_000, 180)

    def test_salario_cero_genera_error(self):
        with self.assertRaises(SalarioInvalidoException):
            calcular_prima(0, 180)

    def test_fecha_invalida_genera_error(self):
        ingreso = datetime(2025, 5, 10)
        retiro = datetime(2025, 2, 10)

        with self.assertRaises(FechaInvalidaException):
            calcular_dias(
                ingreso,
                retiro
            )

    def test_tipo_retiro_invalido_genera_error(self):
        ingreso = datetime(2025, 1, 1)
        retiro = datetime(2025, 12, 1)

        with self.assertRaises(TipoRetiroInvalidoException):
            calcular_liquidacion(
                "Vacaciones",
                2_000_000,
                ingreso,
                retiro,
                0
            )


# ==========================
# EJECUTAR PRUEBAS
# ==========================

if __name__ == "__main__":
    unittest.main(verbosity=2)