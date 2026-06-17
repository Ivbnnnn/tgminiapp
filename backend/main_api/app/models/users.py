from datetime import datetime, timezone, date

from sqlalchemy import Numeric, ForeignKey, Integer, String, Boolean, Date, false, DateTime 
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Agent(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    telegram_id: Mapped[int] = mapped_column(Integer)
    firstname: Mapped[str] = mapped_column(String(255), nullable=False)
    middlename: Mapped[str] = mapped_column(String(255), nullable=True)
    phone:Mapped[str] = mapped_column(String(20), nullable=False)
    email:Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash:Mapped[str] = mapped_column(String(255), nullable=False)
    passport_serial:Mapped[str] = mapped_column(String(20), nullable=False)
    passport_number:Mapped[str] = mapped_column(String(20), nullable=False)
    passport_issue_date:Mapped[datetime] = mapped_column(        DateTime(timezone=True),        nullable=True,    )
    passport_issuer:Mapped[str] = mapped_column(String(255), nullable=False)
    passport_code:Mapped[str] = mapped_column(String(20), nullable=False)
    birthdate:Mapped[date] = mapped_column(        Date,        nullable=True,    )
    status:Mapped[str] = mapped_column(String(255), nullable=False) #individual / self_employed / ip
    inn:Mapped[str] = mapped_column(String(255), nullable=False)
    ogrnip:Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified:Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

