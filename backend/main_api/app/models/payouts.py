from datetime import datetime, timezone, date

from sqlalchemy import Numeric, ForeignKey, Integer, String, Boolean, Date, false, DateTime 
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Payout(Base):
    __tablename__ = "payouts"
    __table_args__ = {"schema": "main_api"}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.agents.id", ondelete="CASCADE"),
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
