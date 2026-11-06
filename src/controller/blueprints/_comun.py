
"""
Elementos compartidos por los Blueprints de la aplicación web.
"""

from flask import current_app

from controller.liquidacion_controller import LiquidacionController

from model.excepciones import (
    ConfiguracionBDError,
    DocumentoInvalidoError,
    EmpleadoNoEncontradoError,
    ErrorConexionBDError,
    FechaInvalidaError,
    LiquidacionNoEncontradaError,
    NombreInvalidoError,
    SalarioInvalidoError,
    TablasNoCreadasError,
    TipoRetiroInvalidoError,
    VacacionesInvalidasError,
)

from model.logica_liquidacion import (
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
    RENUNCIA,
)


TIPOS_RETIRO = [
    RENUNCIA,
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
]


ERRORES_PARA_EL_USUARIO = (
    ValueError,
    ConfiguracionBDError,
    DocumentoInvalidoError,
    EmpleadoNoEncontradoError,
    ErrorConexionBDError,
    FechaInvalidaError,
    LiquidacionNoEncontradaError,
    NombreInvalidoError,
    SalarioInvalidoError,
    TablasNoCreadasError,
    TipoRetiroInvalidoError,
    VacacionesInvalidasError,
)


def obtener_controlador() -> LiquidacionController:
    """Obtiene el controlador de liquidaciones de la aplicación."""

    if "controlador" not in current_app.extensions:
        current_app.extensions["controlador"] = LiquidacionController()

    return current_app.extensions["controlador"]
