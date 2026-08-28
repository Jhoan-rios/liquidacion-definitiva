"""
Excepciones personalizadas para la liquidación laboral.
"""


class FechaInvalidaError(Exception):
    """Se genera cuando una fecha de retiro es inválida."""

    def __init__(self):
        super().__init__(
            "La fecha de retiro es inválida."
        )


class SalarioInvalidoError(Exception):
    """Se genera cuando el salario no es válido."""

    def __init__(self):
        super().__init__(
            "El salario debe ser mayor que cero."
        )


class TipoRetiroInvalidoError(Exception):
    """Se genera cuando el tipo de retiro no es válido."""

    def __init__(self):
        super().__init__(
            "Tipo de retiro inválido."
        )


class VacacionesInvalidasError(Exception):
    """Se genera cuando los días de vacaciones no son válidos."""

    def __init__(self):
        super().__init__(
            "Los días de vacaciones disfrutadas "
            "no pueden ser negativos."
        )