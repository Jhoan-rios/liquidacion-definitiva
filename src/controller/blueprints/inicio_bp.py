
"""
Rutas principales de la aplicación web.
"""

from flask import Blueprint, render_template

from controller.blueprints._comun import obtener_controlador


inicio_bp = Blueprint("inicio", __name__)


@inicio_bp.route("/")
def inicio():
    """Muestra el resumen de la aplicación."""

    controlador = obtener_controlador()

    liquidaciones = controlador.listar_liquidaciones(limite=5)
    empleados = controlador.listar_empleados()

    return render_template(
        "inicio.html",
        liquidaciones=liquidaciones,
        empleados=empleados,
    )
