"""
Interfaz de consola para el cálculo de liquidación laboral.

Solicita los datos al usuario, invoca la lógica de negocio
(logica_liquidacion.py) y muestra el resultado o el error
correspondiente.
"""

from datetime import datetime

from logica_liquidacion import (
    calcular_liquidacion,
    SalarioInvalidoException,
    FechaInvalidaException,
    TipoRetiroInvalidoException,
    VacacionesInvalidasException,
)


def pedir_fecha(mensaje):
    while True:
        texto = input(mensaje)
        try:
            return datetime.strptime(texto, "%Y-%m-%d")
        except ValueError:
            print("Formato inválido. Usa AAAA-MM-DD (ej: 2025-01-31).")


def pedir_numero(mensaje):
    while True:
        texto = input(mensaje)
        try:
            return float(texto)
        except ValueError:
            print("Debes ingresar un número válido.")


def pedir_entero(mensaje):
    while True:
        texto = input(mensaje)
        try:
            return int(texto)
        except ValueError:
            print("Debes ingresar un número entero válido.")


def pedir_tipo_retiro():
    opciones = [
        "Renuncia",
        "Despido con justa causa",
        "Despido sin justa causa",
    ]
    print("Tipos de retiro disponibles:")
    for i, opcion in enumerate(opciones, start=1):
        print(f"  {i}. {opcion}")

    while True:
        texto = input("Selecciona el número del tipo de retiro: ")
        if texto.isdigit() and 1 <= int(texto) <= len(opciones):
            return opciones[int(texto) - 1]
        print("Opción inválida, intenta de nuevo.")


def main():
    print("=== Calculadora de Liquidación Laboral ===\n")

    tipo_retiro = pedir_tipo_retiro()
    salario = pedir_numero("Salario mensual: ")
    fecha_ingreso = pedir_fecha("Fecha de ingreso (AAAA-MM-DD): ")
    fecha_retiro = pedir_fecha("Fecha de retiro (AAAA-MM-DD): ")
    vacaciones_disfrutadas = pedir_entero("Días de vacaciones ya disfrutados: ")

    try:
        resultado = calcular_liquidacion(
            tipo_retiro,
            salario,
            fecha_ingreso,
            fecha_retiro,
            vacaciones_disfrutadas,
        )
        print(f"\nEl valor total de la liquidación es: ${resultado:,.2f}")

    except SalarioInvalidoException as e:
        print(f"\nError de salario: {e}")
    except FechaInvalidaException as e:
        print(f"\nError de fecha: {e}")
    except TipoRetiroInvalidoException as e:
        print(f"\nError de tipo de retiro: {e}")
    except VacacionesInvalidasException as e:
        print(f"\nError de vacaciones: {e}")


if __name__ == "__main__":
    main()