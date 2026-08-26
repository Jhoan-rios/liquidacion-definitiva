"""
Interfaz de consola para el cálculo de liquidación laboral.
"""

from datetime import datetime

from model.excepciones import (
    FechaInvalidaError,
    SalarioInvalidoError,
    TipoRetiroInvalidoError,
    VacacionesInvalidasError,
)

from model.logica_liquidacion import (
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
    RENUNCIA,
    calcular_liquidacion,
)


FORMATO_FECHA = "%Y-%m-%d"

TIPOS_RETIRO = [
    RENUNCIA,
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
]


def pedir_fecha(mensaje: str) -> datetime:
    """Solicita una fecha válida al usuario."""

    while True:
        texto_fecha = input(mensaje)

        try:
            return datetime.strptime(
                texto_fecha,
                FORMATO_FECHA,
            )
        except ValueError:
            print(
                "Formato inválido. "
                "Usa AAAA-MM-DD (ej: 2025-01-31)."
            )


def pedir_numero(mensaje: str) -> float:
    """Solicita un número decimal válido al usuario."""

    while True:
        texto_numero = input(mensaje)

        try:
            return float(texto_numero)
        except ValueError:
            print("Debes ingresar un número válido.")


def pedir_entero(mensaje: str) -> int:
    """Solicita un número entero válido al usuario."""

    while True:
        texto_entero = input(mensaje)

        try:
            return int(texto_entero)
        except ValueError:
            print("Debes ingresar un número entero válido.")


def pedir_tipo_retiro() -> str:
    """Solicita al usuario el tipo de retiro."""

    mostrar_tipos_retiro()

    while True:
        opcion_seleccionada = input(
            "Selecciona el número del tipo de retiro: "
        )

        if opcion_seleccionada.isdigit():
            indice = int(opcion_seleccionada) - 1

            if 0 <= indice < len(TIPOS_RETIRO):
                return TIPOS_RETIRO[indice]

        print("Opción inválida, intenta de nuevo.")


def mostrar_tipos_retiro() -> None:
    """Muestra las opciones de tipo de retiro."""

    print("Tipos de retiro disponibles:")

    for indice, tipo_retiro in enumerate(
        TIPOS_RETIRO,
        start=1,
    ):
        print(f"  {indice}. {tipo_retiro}")


def mostrar_resultado(resultado: float) -> None:
    """Muestra el resultado de la liquidación."""

    print(
        f"\nEl valor total de la liquidación es: "
        f"${resultado:,.2f}"
    )


def mostrar_error(mensaje: str) -> None:
    """Muestra un mensaje de error."""

    print(f"\n{mensaje}")


def main() -> None:
    """Ejecuta el flujo principal de la aplicación."""

    print("=== Calculadora de Liquidación Laboral ===\n")

    tipo_retiro = pedir_tipo_retiro()
    salario = pedir_numero("Salario mensual: ")
    fecha_ingreso = pedir_fecha(
        "Fecha de ingreso (AAAA-MM-DD): "
    )
    fecha_retiro = pedir_fecha(
        "Fecha de retiro (AAAA-MM-DD): "
    )
    vacaciones_disfrutadas = pedir_entero(
        "Días de vacaciones ya disfrutados: "
    )

    try:
        resultado = calcular_liquidacion(
            tipo_retiro,
            salario,
            fecha_ingreso,
            fecha_retiro,
            vacaciones_disfrutadas,
        )

        mostrar_resultado(resultado)

    except SalarioInvalidoError as error:
        mostrar_error(f"Error de salario: {error}")

    except FechaInvalidaError as error:
        mostrar_error(f"Error de fecha: {error}")

    except TipoRetiroInvalidoError as error:
        mostrar_error(f"Error de tipo de retiro: {error}")

    except VacacionesInvalidasError as error:
        mostrar_error(f"Error de vacaciones: {error}")


if __name__ == "__main__":
    main()