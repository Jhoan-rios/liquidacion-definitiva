
"""
Rutas para consultar las operaciones de base de datos.
"""

from flask import Blueprint, flash, redirect, render_template, url_for

from controller.blueprints._comun import (
    ERRORES_PARA_EL_USUARIO,
    obtener_controlador,
)

from model.excepciones import TablasNoCreadasError

base_datos_bp = Blueprint("base_datos", __name__)

@base_datos_bp.route("/base-datos")
def base_datos():
    """Muestra los empleados y las liquidaciones registradas."""

    empleados = []
    liquidaciones = []

    try:
        controlador = obtener_controlador()
        empleados = controlador.listar_empleados()
        liquidaciones = controlador.listar_liquidaciones()
    except TablasNoCreadasError:
        flash(
            "Aún no existen las tablas. Pulsa «Crear tablas» para comenzar.",
            "info",
        )
    except ERRORES_PARA_EL_USUARIO as error:
        flash(str(error), "error")

    return render_template(
        "base_datos.html",
        empleados=empleados,
        liquidaciones=liquidaciones,
    )

@base_datos_bp.route("/base-datos/crear", methods=["POST"])
def crear_tablas():
    """Crea las tablas que aún no existen."""

    try:
        obtener_controlador().crear_tablas()
        flash("Las tablas están creadas y listas para usar.", "exito")
    except ERRORES_PARA_EL_USUARIO as error:
        flash(str(error), "error")

    return redirect(url_for("base_datos.base_datos"))

@base_datos_bp.route(
    "/base-datos/empleados/<string:documento>/eliminar",
    methods=["POST"],
)

def eliminar_empleado(documento):
    """Elimina un empleado solo si no tiene liquidaciones asociadas."""

    try:
        controlador = obtener_controlador()
        empleados = controlador.listar_empleados()

        empleado = next(
            (
                registro
                for registro in empleados
                if registro["documento"] == documento
            ),
            None,
        )

        if empleado and empleado["cantidad_liquidaciones"] > 0:
            flash(
                "No se puede eliminar este empleado porque tiene liquidaciones asociadas.",
                "error",
            )
        else:
            controlador.eliminar_empleado(documento)
            flash("El empleado fue eliminado.", "exito")

    except ERRORES_PARA_EL_USUARIO as error:
        flash(str(error), "error")

    return redirect(url_for("base_datos.base_datos"))
