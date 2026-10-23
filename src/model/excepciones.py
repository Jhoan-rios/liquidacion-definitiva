"""
Excepciones específicas del dominio de liquidación laboral.
"""


class SalarioInvalidoError(Exception):
    """Se genera cuando el salario no es válido."""

    def __init__(self):
        super().__init__(
            "El salario debe ser mayor que cero."
        )


class FechaInvalidaError(Exception):
    """Se genera cuando la fecha de retiro no es válida."""

    def __init__(self):
        super().__init__(
            "La fecha de retiro es inválida."
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

class DocumentoInvalidoError(Exception):
    """Se genera cuando el documento del empleado no es válido."""

    def __init__(self):
        super().__init__(
            "El documento no puede estar vacío, tener espacios "
            "ni símbolos, y admite máximo 20 caracteres."
        )


class NombreInvalidoError(Exception):
    """Se genera cuando el nombre del empleado no es válido."""

    def __init__(self):
        super().__init__(
            "El nombre del empleado no puede estar vacío "
            "y admite máximo 100 caracteres."
        )


class EmpleadoNoEncontradoError(Exception):
    """Se genera cuando no existe un empleado con ese documento."""

    def __init__(self, documento: str):
        super().__init__(
            f"No existe un empleado con documento {documento}."
        )


class LiquidacionNoEncontradaError(Exception):
    """Se genera cuando no existe una liquidación con ese id."""

    def __init__(self, id_liquidacion: int):
        super().__init__(
            f"No existe una liquidación con id {id_liquidacion}."
        )


class ConfiguracionBDError(Exception):
    """Se genera cuando falta o es inválida la configuración secreta."""

    def __init__(self, detalle: str = ""):
        super().__init__(
            (detalle + " " if detalle else "")
            + "No se encontró una configuración válida. Crea un "
            "archivo .env en la raíz del proyecto (modelo: "
            ".env.example) o copia src/secret_config_sample.py como "
            "src/secret_config.py y completa tus datos de conexión."
        )


class ErrorConexionBDError(Exception):
    """Se genera cuando no es posible usar la base de datos."""

    def __init__(self):
        super().__init__(
            "No se pudo conectar con la base de datos. Revisa "
            "src/secret_config.py y que el servidor esté disponible."
        )


class TablasNoCreadasError(Exception):
    """Se genera cuando se usa la base de datos sin sus tablas."""

    def __init__(self):
        super().__init__(
            "Las tablas no existen en la base de datos. "
            "Créalas primero (opción 4 del menú)."
        )
