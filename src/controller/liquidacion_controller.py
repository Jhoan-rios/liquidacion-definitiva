"""
Controller: coordina la lógica de negocio con la base de datos.
"""

from contextlib import contextmanager
from decimal import Decimal
from typing import NoReturn

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.orm import joinedload, sessionmaker

from model.base_datos import Base, crear_engine
from model.entidades import Empleado, Liquidacion
from model.excepciones import (
    DocumentoInvalidoError,
    EmpleadoNoEncontradoError,
    ErrorConexionBDError,
    LiquidacionNoEncontradaError,
    NombreInvalidoError,
    TablasNoCreadasError,
    TipoRetiroInvalidoError,
)
from model.logica_liquidacion import (
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
    RENUNCIA,
    DatosLiquidacion,
    calcular_conceptos_liquidacion,
    sumar_conceptos_liquidacion,
)


LONGITUD_MAXIMA_DOCUMENTO = 20
LONGITUD_MAXIMA_NOMBRE = 100

CODIGO_POSTGRES_TABLA_NO_EXISTE = "42P01"

TIPOS_RETIRO_VALIDOS = {
    RENUNCIA,
    DESPIDO_CON_JUSTA_CAUSA,
    DESPIDO_SIN_JUSTA_CAUSA,
}


def validar_documento(documento: str) -> str:
    """Valida el documento y lo devuelve sin espacios alrededor."""

    documento = (documento or "").strip()

    if (
        not documento
        or not documento.isalnum()
        or len(documento) > LONGITUD_MAXIMA_DOCUMENTO
    ):
        raise DocumentoInvalidoError()

    return documento


def validar_nombre(nombre: str) -> str:
    """Valida el nombre y lo devuelve sin espacios alrededor."""

    nombre = (nombre or "").strip()

    if not nombre or len(nombre) > LONGITUD_MAXIMA_NOMBRE:
        raise NombreInvalidoError()

    return nombre


def a_decimal(valor: float) -> Decimal:
    """Redondea a dos decimales para guardar en columnas NUMERIC."""

    return Decimal(str(round(valor, 2)))


def relanzar_como_error_de_dominio(error: DBAPIError) -> NoReturn:
    """Convierte errores técnicos de la BD en excepciones propias."""

    if isinstance(error, OperationalError):
        raise ErrorConexionBDError() from error

    codigo = getattr(error.orig, "pgcode", None)

    if codigo == CODIGO_POSTGRES_TABLA_NO_EXISTE:
        raise TablasNoCreadasError() from error

    raise error


class LiquidacionController:
    """Operaciones sobre la base de datos de liquidaciones."""

    def __init__(self, engine: Engine | None = None):
        self._engine = engine or crear_engine()
        self._crear_sesion = sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    def crear_tablas(self) -> None:
        """Crea las tablas si todavía no existen."""

        try:
            Base.metadata.create_all(self._engine)
        except DBAPIError as error:
            relanzar_como_error_de_dominio(error)

    def borrar_tablas(self) -> None:
        """Borra las tablas y todos sus datos."""

        try:
            Base.metadata.drop_all(self._engine)
        except DBAPIError as error:
            relanzar_como_error_de_dominio(error)

    def registrar_liquidacion(
        self,
        documento: str,
        nombre: str,
        datos: DatosLiquidacion,
    ) -> dict:
        """Calcula la liquidación y la guarda (INSERT INTO).

        Si el empleado ya existe (mismo documento) se reutiliza y se
        conserva su nombre original; si no, se crea.
        """

        documento = validar_documento(documento)
        nombre = validar_nombre(nombre)

        # Se calcula antes de abrir la sesión: si los datos son
        # inválidos se lanza la excepción de dominio y no se toca la BD.
        conceptos = calcular_conceptos_liquidacion(datos)
        total = sumar_conceptos_liquidacion(conceptos)

        try:
            with self._crear_sesion.begin() as sesion:
                empleado = self._buscar_empleado(sesion, documento)

                if empleado is None:
                    empleado = Empleado(
                        documento=documento,
                        nombre=nombre,
                    )

                liquidacion = Liquidacion(
                    empleado=empleado,
                    tipo_retiro=datos.tipo_retiro,
                    salario=a_decimal(datos.salario),
                    fecha_ingreso=datos.fecha_ingreso.date(),
                    fecha_retiro=datos.fecha_retiro.date(),
                    vacaciones_disfrutadas=datos.vacaciones_disfrutadas,
                    salario_restante=a_decimal(conceptos.salario_restante),
                    prima=a_decimal(conceptos.prima),
                    cesantias=a_decimal(conceptos.cesantias),
                    intereses=a_decimal(conceptos.intereses),
                    vacaciones=a_decimal(conceptos.vacaciones),
                    indemnizacion=a_decimal(conceptos.indemnizacion),
                    total=a_decimal(total),
                )

                sesion.add(liquidacion)
                sesion.flush()

                return liquidacion.a_diccionario()

        except DBAPIError as error:
            relanzar_como_error_de_dominio(error)

    def buscar_por_documento(self, documento: str) -> list[dict]:
        """Devuelve las liquidaciones de un empleado (SELECT)."""

        documento = validar_documento(documento)

        try:
            with self._crear_sesion() as sesion:
                empleado = self._buscar_empleado(sesion, documento)

                if empleado is None:
                    raise EmpleadoNoEncontradoError(documento)

                consulta = (
                    select(Liquidacion)
                    .options(joinedload(Liquidacion.empleado))
                    .where(Liquidacion.empleado_id == empleado.id)
                    .order_by(Liquidacion.id)
                )

                liquidaciones = sesion.scalars(consulta).all()

                return [
                    liquidacion.a_diccionario()
                    for liquidacion in liquidaciones
                ]

        except DBAPIError as error:
            relanzar_como_error_de_dominio(error)

    def buscar_por_id(self, id_liquidacion: int) -> dict:
        """Devuelve una liquidación por su id (SELECT)."""

        try:
            with self._crear_sesion() as sesion:
                consulta = (
                    select(Liquidacion)
                    .options(joinedload(Liquidacion.empleado))
                    .where(Liquidacion.id == id_liquidacion)
                )

                liquidacion = sesion.scalars(consulta).first()

                if liquidacion is None:
                    raise LiquidacionNoEncontradaError(id_liquidacion)

                return liquidacion.a_diccionario()

        except DBAPIError as error:
            relanzar_como_error_de_dominio(error)

    # ------------------------------------------------------------------
    # Funcionalidades adicionales
    # ------------------------------------------------------------------

    def listar_liquidaciones(self, limite: int | None = None) -> list[dict]:
        """Devuelve todas las liquidaciones, de la más reciente a la más antigua."""

        consulta = (
            select(Liquidacion)
            .options(joinedload(Liquidacion.empleado))
            .order_by(Liquidacion.id.desc())
            .limit(limite)
        )

        with self._sesion() as sesion:
            return [
                liquidacion.a_diccionario()
                for liquidacion in sesion.scalars(consulta).all()
            ]

    def buscar_por_tipo_retiro(self, tipo_retiro: str) -> list[dict]:
        """Devuelve las liquidaciones de un tipo de retiro (puede ser vacío)."""

        if tipo_retiro not in TIPOS_RETIRO_VALIDOS:
            raise TipoRetiroInvalidoError()

        consulta = (
            select(Liquidacion)
            .options(joinedload(Liquidacion.empleado))
            .where(Liquidacion.tipo_retiro == tipo_retiro)
            .order_by(Liquidacion.id)
        )

        with self._sesion() as sesion:
            return [
                liquidacion.a_diccionario()
                for liquidacion in sesion.scalars(consulta).all()
            ]

    def listar_empleados(self) -> list[dict]:
        """Devuelve los empleados con su cantidad de liquidaciones."""

        consulta = (
            select(Empleado, func.count(Liquidacion.id))
            .outerjoin(Liquidacion)
            .group_by(Empleado.id)
            .order_by(Empleado.id)
        )

        with self._sesion() as sesion:
            return [
                {
                    "id": empleado.id,
                    "documento": empleado.documento,
                    "nombre": empleado.nombre,
                    "cantidad_liquidaciones": cantidad,
                }
                for empleado, cantidad in sesion.execute(consulta).all()
            ]

    def obtener_total_liquidado(self, documento: str) -> float:
        """Suma el total de todas las liquidaciones de un empleado."""

        documento = validar_documento(documento)

        with self._sesion() as sesion:
            empleado = self._buscar_empleado(sesion, documento)

            if empleado is None:
                raise EmpleadoNoEncontradoError(documento)

            suma = sesion.scalar(
                select(func.coalesce(func.sum(Liquidacion.total), 0))
                .where(Liquidacion.empleado_id == empleado.id)
            )

            return float(suma)

    def actualizar_nombre_empleado(self, documento: str, nombre: str) -> dict:
        """Cambia el nombre de un empleado (UPDATE)."""

        documento = validar_documento(documento)
        nombre = validar_nombre(nombre)

        with self._sesion() as sesion:
            empleado = self._buscar_empleado(sesion, documento)

            if empleado is None:
                raise EmpleadoNoEncontradoError(documento)

            empleado.nombre = nombre

            return {
                "id": empleado.id,
                "documento": empleado.documento,
                "nombre": empleado.nombre,
            }

    def eliminar_liquidacion(self, id_liquidacion: int) -> None:
        """Elimina una liquidación por su id (DELETE)."""

        with self._sesion() as sesion:
            liquidacion = sesion.get(Liquidacion, id_liquidacion)

            if liquidacion is None:
                raise LiquidacionNoEncontradaError(id_liquidacion)

            sesion.delete(liquidacion)

    def eliminar_empleado(self, documento: str) -> int:
        """Elimina un empleado y sus liquidaciones; devuelve cuántas se borraron."""

        documento = validar_documento(documento)

        with self._sesion() as sesion:
            empleado = self._buscar_empleado(sesion, documento)

            if empleado is None:
                raise EmpleadoNoEncontradoError(documento)

            borradas = len(empleado.liquidaciones)
            sesion.delete(empleado)

            return borradas

    @contextmanager
    def _sesion(self):
        """Sesión con commit automático que traduce los errores de la BD."""

        try:
            with self._crear_sesion.begin() as sesion:
                yield sesion
        except DBAPIError as error:
            relanzar_como_error_de_dominio(error)

    @staticmethod
    def _buscar_empleado(sesion, documento: str) -> Empleado | None:
        """Busca un empleado por documento dentro de una sesión."""

        consulta = select(Empleado).where(
            Empleado.documento == documento
        )

        return sesion.scalars(consulta).first()
