from datetime import datetime, timezone, date
from decimal import Decimal

from sqlalchemy import Numeric, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Commission(Base):
    __tablename__ = "commissions"
    __table_args__ = {"schema": "main_api"}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.agents.id"),
        nullable=False,
    )

    insurance_company_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    calculation_id: Mapped[int | None] = mapped_column(
        ForeignKey("main_api.calculations.id"),
        nullable=False,
    )

    policy_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    percent: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )