"""
Lógica de negocio para el cálculo de la liquidación laboral.
"""

from datetime import datetime

from model.excepciones import (
    FechaInvalidaError,
    SalarioInvalidoError,
    TipoRetiroInvalidoError,
    VacacionesInvalidasError,
)


# Constantes de cálculo
DIAS_DEL_ANO = 360
DIAS_DEL_MES = 30
TASA_INTERESES_CESANTIAS = 0.12

DIAS_INDEMNIZACION_BASE = 30
DIAS_INDEMNIZACION_POR_ANO_ADICIONAL = 20

RENUNCIA = "Renuncia"
DESPIDO_CON_JUSTA_CAUSA = "Despido con justa causa"
DESPIDO_SIN_JUSTA_CAUSA = "Despido sin justa causa"

TIPOS_RETIRO_SIN_INDEMNIZACION = {
    RENUNCIA,
    DESPIDO_CON_JUSTA_CAUSA,
}


def validar_salario(salario: float) -> None:
    """Valida que el salario sea mayor que cero."""

    if salario <= 0:
        raise SalarioInvalidoError(
            "El salario debe ser mayor que cero."
        )


def validar_vacaciones_disfrutadas(
    vacaciones_disfrutadas: int,
) -> None:
    """Valida que los días de vacaciones no sean negativos."""

    if vacaciones_disfrutadas < 0:
        raise VacacionesInvalidasError(
            "Los días de vacaciones disfrutadas "
            "no pueden ser negativos."
        )


def calcular_dias_trabajados(
    fecha_ingreso: datetime,
    fecha_retiro: datetime,
) -> int:
    """Calcula la cantidad de días trabajados."""

    if fecha_retiro is None or fecha_retiro < fecha_ingreso:
        raise FechaInvalidaError(
            "La fecha de retiro es inválida."
        )

    return (fecha_retiro - fecha_ingreso).days


def calcular_salario_restante(
    salario: float,
    fecha_retiro: datetime,
) -> float:
    """Calcula el salario correspondiente al último período trabajado."""

    validar_salario(salario)

    dias_trabajados_del_mes = fecha_retiro.day

    return (
        salario / DIAS_DEL_MES
    ) * dias_trabajados_del_mes


def calcular_prima(
    salario: float,
    dias_trabajados: int,
) -> float:
    """Calcula el valor proporcional de la prima."""

    validar_salario(salario)

    return calcular_proporcion_anual(
        salario,
        dias_trabajados,
    )


def calcular_cesantias(
    salario: float,
    dias_trabajados: int,
) -> float:
    """Calcula el valor proporcional de las cesantías."""

    validar_salario(salario)

    return calcular_proporcion_anual(
        salario,
        dias_trabajados,
    )


def calcular_proporcion_anual(
    salario: float,
    dias_trabajados: int,
) -> float:
    """Calcula un concepto proporcional a los días trabajados."""

    return (
        salario * dias_trabajados
    ) / DIAS_DEL_ANO


def calcular_intereses(
    cesantias: float,
    dias_trabajados: int,
) -> float:
    """Calcula los intereses sobre las cesantías."""

    return (
        cesantias
        * TASA_INTERESES_CESANTIAS
        * dias_trabajados
    ) / DIAS_DEL_ANO


def calcular_vacaciones(
    salario: float,
    dias_trabajados: int,
    vacaciones_disfrutadas: int,
) -> float:
    """Calcula el valor de las vacaciones pendientes."""

    validar_salario(salario)
    validar_vacaciones_disfrutadas(vacaciones_disfrutadas)

    vacaciones_generadas = calcular_vacaciones_generadas(
        salario,
        dias_trabajados,
    )

    valor_vacaciones_disfrutadas = calcular_valor_vacaciones_disfrutadas(
        salario,
        vacaciones_disfrutadas,
    )

    vacaciones_pendientes = (
        vacaciones_generadas
        - valor_vacaciones_disfrutadas
    )

    return max(vacaciones_pendientes, 0)


def calcular_vacaciones_generadas(
    salario: float,
    dias_trabajados: int,
) -> float:
    """Calcula el valor de vacaciones generado durante el período."""

    return (
        salario * dias_trabajados
    ) / (DIAS_DEL_ANO * 2)


def calcular_valor_vacaciones_disfrutadas(
    salario: float,
    vacaciones_disfrutadas: int,
) -> float:
    """Calcula el valor de las vacaciones ya disfrutadas."""

    return (
        salario / DIAS_DEL_MES
    ) * vacaciones_disfrutadas


def calcular_indemnizacion(
    salario: float,
    dias_trabajados: int,
) -> float:
    """Calcula la indemnización por despido sin justa causa."""

    validar_salario(salario)

    salario_diario = salario / DIAS_DEL_MES
    dias_indemnizacion = calcular_dias_indemnizacion(
        dias_trabajados
    )

    return salario_diario * dias_indemnizacion


def calcular_dias_indemnizacion(
    dias_trabajados: int,
) -> float:
    """Calcula los días que corresponden a la indemnización."""

    dias_indemnizacion = DIAS_INDEMNIZACION_BASE

    if dias_trabajados <= DIAS_DEL_ANO:
        return dias_indemnizacion

    dias_excedentes = dias_trabajados - DIAS_DEL_ANO

    anos_completos = dias_excedentes // DIAS_DEL_ANO

    dias_indemnizacion += (
        anos_completos
        * DIAS_INDEMNIZACION_POR_ANO_ADICIONAL
    )

    dias_excedentes_del_ultimo_ano = (
        dias_excedentes % DIAS_DEL_ANO
    )

    dias_indemnizacion += (
        dias_excedentes_del_ultimo_ano
        * DIAS_INDEMNIZACION_POR_ANO_ADICIONAL
    ) / DIAS_DEL_ANO

    return dias_indemnizacion


def calcular_indemnizacion_por_tipo_retiro(
    tipo_retiro: str,
    salario: float,
    dias_trabajados: int,
) -> float:
    """Calcula la indemnización según el tipo de retiro."""

    if tipo_retiro in TIPOS_RETIRO_SIN_INDEMNIZACION:
        return 0

    if tipo_retiro == DESPIDO_SIN_JUSTA_CAUSA:
        return calcular_indemnizacion(
            salario,
            dias_trabajados,
        )

    raise TipoRetiroInvalidoError(
        "Tipo de retiro inválido."
    )


def calcular_liquidacion(
    tipo_retiro: str,
    salario: float,
    fecha_ingreso: datetime,
    fecha_retiro: datetime,
    vacaciones_disfrutadas: int,
) -> float:
    """Calcula el valor total de la liquidación laboral."""

    dias_trabajados = calcular_dias_trabajados(
        fecha_ingreso,
        fecha_retiro,
    )

    salario_restante = calcular_salario_restante(
        salario,
        fecha_retiro,
    )

    prima = calcular_prima(
        salario,
        dias_trabajados,
    )

    cesantias = calcular_cesantias(
        salario,
        dias_trabajados,
    )

    intereses = calcular_intereses(
        cesantias,
        dias_trabajados,
    )

    vacaciones = calcular_vacaciones(
        salario,
        dias_trabajados,
        vacaciones_disfrutadas,
    )

    indemnizacion = calcular_indemnizacion_por_tipo_retiro(
        tipo_retiro,
        salario,
        dias_trabajados,
    )

    return sumar_conceptos_liquidacion(
        salario_restante,
        prima,
        cesantias,
        intereses,
        vacaciones,
        indemnizacion,
    )


def sumar_conceptos_liquidacion(
    salario_restante: float,
    prima: float,
    cesantias: float,
    intereses: float,
    vacaciones: float,
    indemnizacion: float,
) -> float:
    """Suma todos los conceptos que componen la liquidación."""

    return (
        salario_restante
        + prima
        + cesantias
        + intereses
        + vacaciones
        + indemnizacion
    )