
"""
Fábrica de la aplicación Flask.

Permite utilizar las mismas rutas y lógica de negocio
con diferentes carpetas de plantillas.
"""

import os
from pathlib import Path

from flask import Flask

from controller.blueprints import registrar_blueprints


def formatear_moneda(valor: float) -> str:
    """Formatea un valor con separadores colombianos."""

    valor_formateado = f"{valor:,.2f}"
    parte_entera, parte_decimal = valor_formateado.rsplit(".", 1)
    parte_entera = parte_entera.replace(",", ".")

    return f"${parte_entera},{parte_decimal}"


def crear_aplicacion(
    carpeta_plantillas: Path,
    carpeta_estaticos: Path | None = None,
    controlador=None,
) -> Flask:
    """Crea y configura la aplicación Flask.

    Args:
        carpeta_plantillas: Ubicación de las plantillas HTML.
        carpeta_estaticos: Ubicación opcional de archivos estáticos.
        controlador: Controlador opcional para las pruebas.

    Returns:
        Aplicación Flask configurada.
    """

    app = Flask(
        __name__,
        template_folder=str(carpeta_plantillas),
        static_folder=(
            str(carpeta_estaticos) if carpeta_estaticos else None
        ),
    )

    clave_secreta = os.environ.get("FLASK_SECRET_KEY")

    if not clave_secreta:
        raise RuntimeError("Falta configurar FLASK_SECRET_KEY.")

    app.config["SECRET_KEY"] = clave_secreta

    if controlador is not None:
        app.extensions["controlador"] = controlador

    app.jinja_env.filters["moneda"] = formatear_moneda

    registrar_blueprints(app)

    return app
