"""
Módulo de lógica de negocio para el cálculo de liquidación laboral.

Contiene las constantes, excepciones personalizadas y funciones de cálculo.
No contiene código de interfaz (consola) ni pruebas unitarias.
"""

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
    if fecha_retiro is None or fecha_retiro < fecha_ingreso:
        raise FechaInvalidaException(
            "La fecha de retiro es inválida."
        )

    return (fecha_retiro - fecha_ingreso).days


def calcular_salario_restante(salario, fecha_retiro):
    validar_salario(salario)

    dias_trabajados_mes = fecha_retiro.day

    return (salario / DIAS_MES) * dias_trabajados_mes


def calcular_prima(salario, dias):
    validar_salario(salario)

    return (salario * dias) / DIAS_ANO


def calcular_cesantias(salario, dias):
    validar_salario(salario)

    return (salario * dias) / DIAS_ANO


def calcular_intereses(cesantias, dias):
    return (
        cesantias
        * PORCENTAJE_INTERESES
        * dias
    ) / DIAS_ANO


def calcular_vacaciones(
    salario,
    dias,
    vacaciones_disfrutadas
):
    validar_salario(salario)

    vacaciones_generadas = (
        salario * dias
    ) / (DIAS_ANO * 2)

    descuento = (
        salario / DIAS_MES
    ) * vacaciones_disfrutadas

    vacaciones_pendientes = (
        vacaciones_generadas - descuento
    )

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
            fraccion
            * DIAS_INDEMNIZACION_ADICIONALES
        ) / DIAS_ANO

    return salario_dia * dias_indemnizacion


def calcular_liquidacion(
    tipo_retiro,
    salario,
    fecha_ingreso,
    fecha_retiro,
    vacaciones_disfrutadas
):
    dias = calcular_dias(
        fecha_ingreso,
        fecha_retiro
    )

    salario_restante = calcular_salario_restante(
        salario,
        fecha_retiro
    )

    prima = calcular_prima(
        salario,
        dias
    )

    cesantias = calcular_cesantias(
        salario,
        dias
    )

    intereses = calcular_intereses(
        cesantias,
        dias
    )

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
        salario_restante
        + prima
        + cesantias
        + intereses
        + vacaciones
        + indemnizacion
    )