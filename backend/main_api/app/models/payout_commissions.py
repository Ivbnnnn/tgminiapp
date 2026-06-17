from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PayoutCommission(Base):
    __tablename__ = "payout_commissions"
    __table_args__ = {"schema": "main_api"}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    payout_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.payouts.id"),
        nullable=False,
    )

    commission_id: Mapped[int] = mapped_column(
        ForeignKey("main_api.commissions.id"),
        nullable=False,
    )