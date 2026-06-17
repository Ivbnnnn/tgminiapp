from datetime import datetime, timezone, date
from decimal import Decimal

from sqlalchemy import Numeric, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CalculationCompanies(Base):
    __tablename__ = "calculation_companies"
    __table_args__ = {"schema": "main_api"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.agents.id"),
        nullable=False,
    )
    calculation_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.calculations.id"),
        nullable=False,
    )

    insurance_company_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )

    policy_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )