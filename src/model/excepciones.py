"""
Excepciones específicas del dominio de liquidación laboral.
"""


class SalarioInvalidoError(Exception):
    """Se genera cuando el salario no es válido."""


class FechaInvalidaError(Exception):
    """Se genera cuando las fechas de ingreso y retiro no son válidas."""


class TipoRetiroInvalidoError(Exception):
    """Se genera cuando el tipo de retiro no está permitido."""


class VacacionesInvalidasError(Exception):
    """Se genera cuando los días de vacaciones disfrutadas no son válidos."""