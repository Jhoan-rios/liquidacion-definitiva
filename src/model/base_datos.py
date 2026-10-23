"""
Configuración de la conexión a PostgreSQL y base declarativa del ORM.
"""

import os
from pathlib import Path
from types import SimpleNamespace

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import DeclarativeBase

from model.excepciones import ConfiguracionBDError


TIEMPO_MAXIMO_CONEXION_SEGUNDOS = 10

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent
RUTA_ENV = RAIZ_PROYECTO / ".env"

VARIABLES_OBLIGATORIAS = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
PUERTO_POSTGRES_POR_DEFECTO = 5432
MODO_SSL_POR_DEFECTO = "require"


class Base(DeclarativeBase):
    """Clase base de todas las entidades del ORM."""


def cargar_configuracion_env(ruta: Path = RUTA_ENV):
    """Lee la configuración del archivo .env (o de variables de entorno).

    Devuelve None si no hay ninguna variable DB_* configurada. Los valores
    del archivo .env tienen prioridad sobre las variables de entorno.
    """

    valores = {
        clave: valor
        for clave, valor in os.environ.items()
        if clave.startswith("DB_")
    }

    if ruta.exists():
        valores.update(
            {
                clave: valor
                for clave, valor in dotenv_values(ruta).items()
                if valor is not None
            }
        )

    if "DB_USER" not in valores and "DB_HOST" not in valores:
        return None

    faltantes = [
        variable
        for variable in VARIABLES_OBLIGATORIAS
        if not valores.get(variable)
    ]

    if faltantes:
        raise ConfiguracionBDError(
            f"Faltan variables en el .env: {', '.join(faltantes)}."
        )

    try:
        puerto = int(
            valores.get("DB_PORT") or PUERTO_POSTGRES_POR_DEFECTO
        )
    except ValueError as error:
        raise ConfiguracionBDError(
            "DB_PORT debe ser un número (por ejemplo 5432)."
        ) from error

    return SimpleNamespace(
        ORIGEN=str(ruta) if ruta.exists() else "variables de entorno",
        DB_USER=valores["DB_USER"].strip(),
        DB_PASSWORD=valores["DB_PASSWORD"],
        DB_HOST=valores["DB_HOST"].strip(),
        DB_PORT=puerto,
        DB_NAME=valores["DB_NAME"].strip(),
        DB_NAME_TEST=(
            valores.get("DB_NAME_TEST") or f"{valores['DB_NAME']}_test"
        ).strip(),
        DB_SSLMODE=(
            valores.get("DB_SSLMODE") or MODO_SSL_POR_DEFECTO
        ).strip(),
    )


def cargar_configuracion_secreta(ruta_env: Path = RUTA_ENV):
    """Carga la configuración de conexión.

    Orden de búsqueda:
      1. El archivo .env en la raíz del proyecto (o variables DB_*).
      2. El archivo src/secret_config.py.
    """

    configuracion = cargar_configuracion_env(ruta_env)

    if configuracion is not None:
        return configuracion

    try:
        import secret_config
    except ModuleNotFoundError as error:
        if error.name != "secret_config":
            raise

        raise ConfiguracionBDError() from error

    return secret_config


def construir_url(nombre_bd: str | None = None) -> URL:
    """Construye la URL de conexión con los datos de secret_config.py.

    Si no se indica nombre_bd se usa DB_NAME. Las pruebas unitarias
    pasan DB_NAME_TEST para no tocar los datos reales.
    """

    config = cargar_configuracion_secreta()

    try:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=int(config.DB_PORT),
            database=nombre_bd or config.DB_NAME,
            query={"sslmode": config.DB_SSLMODE},
        )
    except AttributeError as error:
        raise ConfiguracionBDError() from error


def crear_engine(url: URL | None = None) -> Engine:
    """Crea el motor de conexión del ORM."""

    return create_engine(
        url or construir_url(),
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": TIEMPO_MAXIMO_CONEXION_SEGUNDOS,
        },
    )
