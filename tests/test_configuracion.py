"""
Pruebas de la lectura de la configuración (.env) y de las
advertencias de verificar_conexion. No necesitan base de datos.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


from model.base_datos import cargar_configuracion_env, construir_url
from model.excepciones import ConfiguracionBDError
from verificar_conexion import advertencias_configuracion


# Mezcla de saltos de línea \n y \r\n, como en un .env editado en Windows
ENV_COMPLETO = (
    "DB_USER=usuario_prueba\n"
    "DB_PASSWORD=p@ss:w/rd#1\r\n"
    "DB_HOST=servidor.ejemplo.com\n"
    "DB_PORT=5432\r\n"
    "\r\n"
    "DB_NAME=Mi-Base_db\n"
    "# comentario\r\n"
    "DB_NAME_TEST=mi-base_test\n"
)


class TestConfiguracionEnv(unittest.TestCase):

    def crear_env(self, contenido: str) -> Path:
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        ruta = Path(carpeta.name) / ".env"
        ruta.write_bytes(contenido.encode("utf-8"))
        return ruta

    def test_lee_todas_las_variables_del_env(self):
        config = cargar_configuracion_env(self.crear_env(ENV_COMPLETO))

        self.assertEqual(config.DB_USER, "usuario_prueba")
        self.assertEqual(config.DB_PASSWORD, "p@ss:w/rd#1")
        self.assertEqual(config.DB_HOST, "servidor.ejemplo.com")
        self.assertEqual(config.DB_PORT, 5432)
        self.assertEqual(config.DB_NAME, "Mi-Base_db")
        self.assertEqual(config.DB_NAME_TEST, "mi-base_test")

    def test_ssl_por_defecto_es_require(self):
        config = cargar_configuracion_env(self.crear_env(ENV_COMPLETO))

        self.assertEqual(config.DB_SSLMODE, "require")

    def test_la_url_escapa_la_contrasena_y_conserva_el_nombre(self):
        config = cargar_configuracion_env(self.crear_env(ENV_COMPLETO))
        url = construir_url_desde(config)

        self.assertEqual(url.password, "p@ss:w/rd#1")
        self.assertEqual(url.database, "Mi-Base_db")
        self.assertNotIn("p@ss", url.render_as_string(hide_password=True))

    def test_sin_db_name_test_se_deriva_de_db_name(self):
        contenido = ENV_COMPLETO.replace("DB_NAME_TEST=mi-base_test\n", "")

        config = cargar_configuracion_env(self.crear_env(contenido))

        self.assertEqual(config.DB_NAME_TEST, "Mi-Base_db_test")

    def test_variable_obligatoria_faltante_falla(self):
        contenido = ENV_COMPLETO.replace("DB_NAME=Mi-Base_db\n", "")

        with self.assertRaises(ConfiguracionBDError):
            cargar_configuracion_env(self.crear_env(contenido))

    def test_puerto_no_numerico_falla(self):
        contenido = ENV_COMPLETO.replace("DB_PORT=5432", "DB_PORT=abc")

        with self.assertRaises(ConfiguracionBDError):
            cargar_configuracion_env(self.crear_env(contenido))


def construir_url_desde(config):
    """Construye la URL como lo hace construir_url, con una config dada."""

    from unittest import mock

    with mock.patch(
        "model.base_datos.cargar_configuracion_secreta",
        return_value=config,
    ):
        return construir_url()


class TestAdvertencias(unittest.TestCase):

    def config(self, **cambios) -> SimpleNamespace:
        datos = dict(
            DB_HOST="dpg-abc-a.oregon-postgres.render.com",
            DB_NAME="liquidacion_db",
            DB_NAME_TEST="liquidacion_db_test",
        )
        datos.update(cambios)
        return SimpleNamespace(**datos)

    def test_configuracion_correcta_no_tiene_advertencias(self):
        self.assertEqual(advertencias_configuracion(self.config()), [])

    def test_detecta_hostname_interno_de_render(self):
        advertencias = advertencias_configuracion(
            self.config(DB_HOST="dpg-db35apugekts739hnpcg-a")
        )

        self.assertEqual(len(advertencias), 1)
        self.assertIn("INTERNO", advertencias[0])

    def test_detecta_base_de_pruebas_peligrosa(self):
        advertencias = advertencias_configuracion(
            self.config(DB_NAME_TEST="liquidacion_db")
        )

        self.assertEqual(len(advertencias), 2)


if __name__ == "__main__":
    unittest.main()
