from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserEvent(Base):
    __tablename__ = "user_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True,
    )

    # view, like, unlike, add_to_cart, remove_from_cart, purchase, search
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)

    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default="{}",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[Optional["User"]] = relationship(
        back_populates="events",
    )
    product: Mapped[Optional["Product"]] = relationship(
        back_populates="events",
    )

    __table_args__ = (
        Index("idx_user_events_user_id", "user_id"),
        Index("idx_user_events_product_id", "product_id"),
        Index("idx_user_events_event_type", "event_type"),
        Index("idx_user_events_created_at", "created_at"),
    )
