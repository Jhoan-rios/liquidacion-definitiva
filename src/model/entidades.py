"""
Clases del Model mapeadas a tablas de PostgreSQL mediante el ORM.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base_datos import Base


class Empleado(Base):
    """Empleado al que se le calculan liquidaciones."""

    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(primary_key=True)
    documento: Mapped[str] = mapped_column(
        String(20),
        unique=True,
    )
    nombre: Mapped[str] = mapped_column(String(100))

    liquidaciones: Mapped[list["Liquidacion"]] = relationship(
        back_populates="empleado",
        cascade="all, delete-orphan",
    )


class Liquidacion(Base):
    """Liquidación definitiva calculada para un empleado."""

    __tablename__ = "liquidaciones"
    __table_args__ = (
        CheckConstraint(
            "salario > 0",
            name="ck_liquidaciones_salario_positivo",
        ),
        CheckConstraint(
            "vacaciones_disfrutadas >= 0",
            name="ck_liquidaciones_vacaciones_no_negativas",
        ),
        CheckConstraint(
            "fecha_retiro >= fecha_ingreso",
            name="ck_liquidaciones_fechas_validas",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(
        ForeignKey("empleados.id", ondelete="CASCADE"),
        index=True,
    )
    tipo_retiro: Mapped[str] = mapped_column(String(40))
    salario: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    fecha_retiro: Mapped[date] = mapped_column(Date)
    vacaciones_disfrutadas: Mapped[int]

    salario_restante: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    prima: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    cesantias: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    intereses: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    vacaciones: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    indemnizacion: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    empleado: Mapped[Empleado] = relationship(
        back_populates="liquidaciones",
    )

    def a_diccionario(self) -> dict:
        """Devuelve los datos de la liquidación listos para mostrar."""

        return {
            "id": self.id,
            "documento": self.empleado.documento,
            "nombre": self.empleado.nombre,
            "tipo_retiro": self.tipo_retiro,
            "salario": float(self.salario),
            "fecha_ingreso": self.fecha_ingreso,
            "fecha_retiro": self.fecha_retiro,
            "vacaciones_disfrutadas": self.vacaciones_disfrutadas,
            "salario_restante": float(self.salario_restante),
            "prima": float(self.prima),
            "cesantias": float(self.cesantias),
            "intereses": float(self.intereses),
            "vacaciones": float(self.vacaciones),
            "indemnizacion": float(self.indemnizacion),
            "total": float(self.total),
            "creada_en": self.creada_en,
        }
