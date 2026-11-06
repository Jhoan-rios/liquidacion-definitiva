
"""
Rutas para buscar liquidaciones y empleados.
"""

from flask import Blueprint, flash, render_template, request

from controller.blueprints._comun import (
    ERRORES_PARA_EL_USUARIO,
    obtener_controlador,
)


busqueda_bp = Blueprint("busqueda", __name__)

@busqueda_bp.route("/buscar", methods=["GET"])
def buscar():
    """Busca liquidaciones por documento del empleado o por ID."""

    criterio = request.args.get("criterio", "documento")
    valor = request.args.get("valor", "").strip()
    liquidaciones = []

    if valor:
        try:
            controlador = obtener_controlador()

            if criterio == "documento":
                liquidaciones = controlador.buscar_por_documento(valor)

            elif criterio == "id":
                if not valor.isdecimal():
                    raise ValueError("El ID debe ser un número entero.")

                liquidaciones = [
                    controlador.buscar_por_id(int(valor))
                ]

            else:
                raise ValueError(
                    "Selecciona si deseas buscar por documento o por ID."
                )

            if not liquidaciones:
                flash("No se encontraron liquidaciones.", "info")

        except ERRORES_PARA_EL_USUARIO as error:
            flash(str(error), "error")

    return render_template(
        "buscar.html",
        liquidaciones=liquidaciones,
        criterio=criterio,
        valor=valor,
    )
