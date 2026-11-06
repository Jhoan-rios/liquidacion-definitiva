"""
Punto de entrada de la versión web con diseño Emerald Finance.
"""
import sys
from pathlib import Path

CARPETA_VISTA = Path(__file__).resolve().parent
CARPETA_SRC = CARPETA_VISTA.parent.parent

if str(CARPETA_SRC) not in sys.path:
    sys.path.insert(0, str(CARPETA_SRC))

from controller.aplicacion import crear_aplicacion

app = crear_aplicacion(
    carpeta_plantillas=CARPETA_VISTA / "templates",
    carpeta_estaticos=CARPETA_VISTA / "static",
)

if __name__ == "__main__":
    app.run(debug=True)
