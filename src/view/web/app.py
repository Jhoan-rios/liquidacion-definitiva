
"""
Punto de entrada de la aplicación web Flask.
"""

import sys
from pathlib import Path


RUTA_SRC = Path(__file__).resolve().parents[2]

if str(RUTA_SRC) not in sys.path:
    sys.path.insert(0, str(RUTA_SRC))


from controller.aplicacion import crear_aplicacion


CARPETA_PLANTILLAS = Path(__file__).resolve().parent / "templates"


app = crear_aplicacion(
    carpeta_plantillas=CARPETA_PLANTILLAS,
)
