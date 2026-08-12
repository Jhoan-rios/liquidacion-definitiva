import unittest
from datetime import datetime


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
# FUNCIONES
# ==========================

def calcularDias(fechaIngreso, fechaRetiro):

    if fechaRetiro < fechaIngreso:
        raise FechaInvalidaException("La fecha de retiro es inválida.")

    return (fechaRetiro - fechaIngreso).days


def calcularPrima(salario, dias):

    if salario <= 0:
        raise SalarioInvalidoException("El salario debe ser mayor que cero.")

    return (salario * dias) / 360


def calcularCesantias(salario, dias):

    if salario <= 0:
        raise SalarioInvalidoException("El salario debe ser mayor que cero.")

    return (salario * dias) / 360


def calcularIntereses(cesantias, dias):

    return (cesantias * 0.12 * dias) / 360


def calcularVacaciones(salario, dias, vacacionesDisfrutadas):

    vacaciones = (salario * dias) / 720

    descuento = (salario / 30) * vacacionesDisfrutadas

    vacaciones = vacaciones - descuento

    if vacaciones < 0:
        vacaciones = 0

    return vacaciones


def calcularIndemnizacion(salario, dias):

    salarioDia = salario / 30

    if dias <= 360:

        diasIndemnizacion = 30

    else:

        diasIndemnizacion = 30

        diasRestantes = dias - 360

        años = diasRestantes // 360

        diasIndemnizacion += años * 20

        fraccion = diasRestantes % 360

        diasIndemnizacion += (fraccion * 20) / 360

    return salarioDia * diasIndemnizacion


def calcularLiquidacion(tipoRetiro, salario, fechaIngreso,
                         fechaRetiro, vacacionesDisfrutadas):

    dias = calcularDias(fechaIngreso, fechaRetiro)

    prima = calcularPrima(salario, dias)

    cesantias = calcularCesantias(salario, dias)

    intereses = calcularIntereses(cesantias, dias)

    vacaciones = calcularVacaciones(salario, dias, vacacionesDisfrutadas)

    if tipoRetiro == "Renuncia":

        indemnizacion = 0

    elif tipoRetiro == "Despido con justa causa":

        indemnizacion = 0

    elif tipoRetiro == "Despido sin justa causa":

        indemnizacion = calcularIndemnizacion(salario, dias)

    else:

        raise TipoRetiroInvalidoException("Tipo de retiro inválido.")

    return prima + cesantias + intereses + vacaciones + indemnizacion


# ==========================
# PRUEBAS UNITARIAS
# ==========================

class LiquidacionTest(unittest.TestCase):

    def test_prima(self):

        salario = 2000000
        dias = 180

        resultado = calcularPrima(salario, dias)

        esperado = 1000000

        self.assertEqual(esperado, resultado)


    def test_cesantias(self):

        salario = 1500000
        dias = 360

        resultado = calcularCesantias(salario, dias)

        esperado = 1500000

        self.assertEqual(esperado, resultado)


    def test_intereses(self):

        cesantias = 1200000
        dias = 360

        resultado = calcularIntereses(cesantias, dias)

        esperado = 144000

        self.assertEqual(esperado, resultado)


    def test_vacaciones(self):

        salario = 1800000
        dias = 360
        vacaciones = 5

        resultado = calcularVacaciones(salario, dias, vacaciones)

        esperado = 900000 - (60000 * 5)

        self.assertEqual(esperado, resultado)


    def test_indemnizacion(self):

        salario = 1800000
        dias = 360

        resultado = calcularIndemnizacion(salario, dias)

        esperado = 1800000

        self.assertEqual(esperado, resultado)


    def test_liquidacion_renuncia(self):

        salario = 2000000

        ingreso = datetime(2025, 1, 1)

        retiro = datetime(2025, 12, 27)

        resultado = calcularLiquidacion(
            "Renuncia",
            salario,
            ingreso,
            retiro,
            0
        )

        self.assertTrue(resultado > 0)


    def test_salario_negativo(self):

        with self.assertRaises(SalarioInvalidoException):

            calcularPrima(-1000000, 180)


    def test_fecha_invalida(self):

        ingreso = datetime(2025, 5, 10)

        retiro = datetime(2025, 2, 10)

        with self.assertRaises(FechaInvalidaException):

            calcularDias(ingreso, retiro)


    def test_tipo_retiro_invalido(self):

        ingreso = datetime(2025, 1, 1)

        retiro = datetime(2025, 12, 1)

        with self.assertRaises(TipoRetiroInvalidoException):

            calcularLiquidacion(
                "Vacaciones",
                2000000,
                ingreso,
                retiro,
                0
            )

if __name__ == "__main__":
    unittest.main(verbosity=2)