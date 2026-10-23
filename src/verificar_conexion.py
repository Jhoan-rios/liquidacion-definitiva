"""
Comprueba que la configuración (.env o secret_config.py) conecta con
PostgreSQL y explica qué corregir si algo falla.

Uso, desde la carpeta raíz del proyecto:

    python src/verificar_conexion.py                  # solo revisa
    python src/verificar_conexion.py --crear-bd-test  # intenta crear la BD de pruebas

Nunca imprime la contraseña.
"""

import sys

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError

from model.base_datos import construir_url, crear_engine
from model.base_datos import cargar_configuracion_secreta
from model.excepciones import ConfiguracionBDError


def advertencias_configuracion(config) -> list[str]:
    """Detecta errores frecuentes en los valores de la configuración."""

    advertencias = []

    if config.DB_HOST.startswith("dpg-") and "." not in config.DB_HOST:
        advertencias.append(
            f"DB_HOST '{config.DB_HOST}' parece el hostname INTERNO de Render "
            "(no tiene punto). Solo funciona entre servicios de Render. "
            "Desde tu computador usa el Hostname EXTERNO: en Render, tu "
            "PostgreSQL > Connections > External Database URL; es algo como "
            "dpg-xxxx-a.<region>-postgres.render.com."
        )

    if not config.DB_NAME_TEST.endswith("_test"):
        advertencias.append(
            f"DB_NAME_TEST '{config.DB_NAME_TEST}' debe terminar en '_test' "
            "(las pruebas borran tablas) y no puede ser igual a DB_NAME."
        )

    if config.DB_NAME_TEST == config.DB_NAME:
        advertencias.append(
            "DB_NAME_TEST y DB_NAME son iguales: las pruebas borrarían "
            "tus datos reales."
        )

    if config.DB_NAME != config.DB_NAME.strip() or " " in config.DB_NAME:
        advertencias.append("DB_NAME contiene espacios.")

    return advertencias


def explicar_error(error: DBAPIError) -> str:
    """Traduce el error de PostgreSQL a una pista concreta."""

    detalle = str(error.orig).strip().splitlines()[0]
    minuscula = detalle.lower()

    if "could not translate host name" in minuscula or "name or service" in minuscula:
        pista = "El DB_HOST no se encuentra. Usa el Hostname EXTERNO de Render."
    elif "password authentication failed" in minuscula:
        pista = "Usuario o contraseña incorrectos (DB_USER / DB_PASSWORD)."
    elif "database" in minuscula and "does not exist" in minuscula:
        pista = "Esa base de datos no existe. Revisa DB_NAME: respeta mayúsculas, guiones y guiones bajos."
    elif "ssl" in minuscula:
        pista = "Problema de SSL. En Render usa DB_SSLMODE=require."
    elif "timeout" in minuscula or "timed out" in minuscula or "refused" in minuscula:
        pista = "No hay respuesta del servidor: revisa DB_HOST (externo), DB_PORT y tu conexión a internet."
    else:
        pista = "Revisa los datos de conexión."

    return f"{detalle}\n      -> {pista}"


def probar_base(nombre: str, url) -> bool:
    """Intenta conectarse a una base de datos y muestra lo que encuentra."""

    engine = crear_engine(url)

    try:
        with engine.connect() as conexion:
            fila = conexion.execute(
                text("SELECT current_database(), current_user, "
                     "split_part(version(), ' ', 2)")
            ).one()
            tablas = sorted(inspect(conexion).get_table_names())

        print(f"   OK  {nombre}: conectado a '{fila[0]}' como '{fila[1]}' "
              f"(PostgreSQL {fila[2]})")
        print(f"       tablas: {', '.join(tablas) if tablas else 'ninguna todavía'}")
        return True

    except DBAPIError as error:
        print(f"   FALLA  {nombre}: {explicar_error(error)}")
        return False

    finally:
        engine.dispose()


def existe_base(url) -> bool:
    """Indica si se puede conectar a esa base de datos."""

    engine = crear_engine(url)

    try:
        with engine.connect():
            return True
    except DBAPIError:
        return False
    finally:
        engine.dispose()


def crear_bd_test(config) -> None:
    """Intenta crear la base de datos de pruebas desde la base principal."""

    if existe_base(construir_url(config.DB_NAME_TEST)):
        print(f"   La base de pruebas '{config.DB_NAME_TEST}' ya existe.")
        return

    engine = create_engine(
        construir_url(config.DB_NAME),
        isolation_level="AUTOCOMMIT",
    )
    nombre = engine.dialect.identifier_preparer.quote(config.DB_NAME_TEST)

    try:
        with engine.connect() as conexion:
            conexion.execute(text(f"CREATE DATABASE {nombre}"))
        print(f"   Base de pruebas '{config.DB_NAME_TEST}' creada.")
    except DBAPIError as error:
        print(f"   No se pudo crear '{config.DB_NAME_TEST}': "
              f"{str(error.orig).strip().splitlines()[0]}")
        print("   Si es un tema de permisos, crea una segunda instancia de "
              "PostgreSQL en Render y usa sus datos para DB_NAME_TEST.")
    finally:
        engine.dispose()


def main() -> int:
    """Revisa la configuración y las conexiones. Devuelve 0 si todo está bien."""

    print("=== Verificación de la conexión a la base de datos ===\n")

    try:
        config = cargar_configuracion_secreta()
    except ConfiguracionBDError as error:
        print(f"FALLA  {error}")
        return 1

    origen = getattr(config, "ORIGEN", "src/secret_config.py")
    print(f"1. Configuración leída de: {origen}")
    print(f"   usuario={config.DB_USER}  host={config.DB_HOST}  "
          f"puerto={config.DB_PORT}")
    print(f"   base={config.DB_NAME}  base_pruebas={config.DB_NAME_TEST}  "
          f"ssl={config.DB_SSLMODE}")
    print(f"   contraseña: definida ({len(config.DB_PASSWORD)} caracteres)")

    advertencias = advertencias_configuracion(config)
    for advertencia in advertencias:
        print(f"   AVISO  {advertencia}")

    print("\n2. Conexión a la base principal")
    principal_ok = probar_base("DB_NAME", construir_url(config.DB_NAME))

    if principal_ok and "--crear-bd-test" in sys.argv:
        print("\n   Creando la base de pruebas...")
        crear_bd_test(config)

    print("\n3. Conexión a la base de pruebas")
    prueba_ok = probar_base(
        "DB_NAME_TEST",
        construir_url(config.DB_NAME_TEST),
    )

    if principal_ok and not prueba_ok:
        print("\n   Si la base de pruebas no existe, ejecuta de nuevo con "
              "--crear-bd-test")

    todo_ok = principal_ok and prueba_ok and not advertencias
    print("\nRESULTADO:", "todo bien vinculado." if todo_ok else "hay cosas por corregir (ver arriba).")

    return 0 if todo_ok else 1


if __name__ == "__main__":
    sys.exit(main())
