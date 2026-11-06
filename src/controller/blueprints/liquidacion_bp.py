
"""
Rutas para registrar y consultar liquidaciones.
"""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from model.logica_liquidacion import DatosLiquidacion

from controller.blueprints._comun import (
    ERRORES_PARA_EL_USUARIO,
    TIPOS_RETIRO,
    obtener_controlador,
)


liquidacion_bp = Blueprint("liquidacion", __name__)


@liquidacion_bp.route("/liquidacion/nueva", methods=["GET", "POST"])
def nueva():
    """Registra una nueva liquidación."""

    if request.method == "POST":
        try:
            datos = DatosLiquidacion(
                tipo_retiro=request.form["tipo_retiro"],
                salario=float(request.form["salario"]),
                fecha_ingreso=datetime.strptime(
                    request.form["fecha_ingreso"],
                    "%Y-%m-%d",
                ),
                fecha_retiro=datetime.strptime(
                    request.form["fecha_retiro"],
                    "%Y-%m-%d",
                ),
                vacaciones_disfrutadas=int(
                    request.form["vacaciones_disfrutadas"]
                ),
            )

            liquidacion = obtener_controlador().registrar_liquidacion(
                documento=request.form["documento"],
                nombre=request.form["nombre"],
                datos=datos,
            )

            flash("Liquidación registrada correctamente.", "success")

            return redirect(
                url_for(
                    "liquidacion.detalle",
                    id_liquidacion=liquidacion["id"],
                )
            )

        except ERRORES_PARA_EL_USUARIO as error:
            flash(str(error), "error")

    return render_template(
        "nueva.html",
        tipos_retiro=TIPOS_RETIRO,
    )


@liquidacion_bp.route("/liquidacion/<int:id_liquidacion>")
def detalle(id_liquidacion):
    """Muestra el detalle de una liquidación."""

    try:
        liquidacion = obtener_controlador().buscar_por_id(
            id_liquidacion
        )

        return render_template(
            "liquidacion.html",
            liquidacion=liquidacion,
        )

    except ERRORES_PARA_EL_USUARIO as error:
        flash(str(error), "error")
        return redirect(url_for("inicio.inicio"))

@liquidacion_bp.route(
    "/liquidacion/<int:id_liquidacion>/eliminar",
    methods=["POST"],
)
def eliminar(id_liquidacion):
    """Elimina una liquidación individual."""

    try:
        obtener_controlador().eliminar_liquidacion(id_liquidacion)
        flash("La liquidación fue eliminada.", "exito")
    except ERRORES_PARA_EL_USUARIO as error:
        flash(str(error), "error")

    return redirect(url_for("inicio.inicio"))
