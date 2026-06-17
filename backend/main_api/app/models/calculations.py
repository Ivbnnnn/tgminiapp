from datetime import datetime, timezone, date
from decimal import Decimal

from sqlalchemy import Numeric, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Calculation(Base):
    __tablename__ = "calculations"
    __table_args__ = {"schema": "main_api"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.agents.id"),
        nullable=False,
    )

    insurance_company_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )

    driver_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    vehicle_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    owner_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    policy_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=None
    )

    status: Mapped[str] = mapped_column( # calculated | waiting_for_payment | paid | canceled
        String(20),
        nullable=False,
    )

    policy_start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    use_period: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )