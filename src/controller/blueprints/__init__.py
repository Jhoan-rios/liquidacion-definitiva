
"""
Registro de los Blueprints de la aplicación web.
"""

from controller.blueprints.base_datos_bp import base_datos_bp
from controller.blueprints.busqueda_bp import busqueda_bp
from controller.blueprints.inicio_bp import inicio_bp
from controller.blueprints.liquidacion_bp import liquidacion_bp


TODOS_LOS_BLUEPRINTS = (
    inicio_bp,
    liquidacion_bp,
    busqueda_bp,
    base_datos_bp,
)


def registrar_blueprints(app) -> None:
    """Registra todas las rutas web en la aplicación Flask."""

    for blueprint in TODOS_LOS_BLUEPRINTS:
        app.register_blueprint(blueprint)
