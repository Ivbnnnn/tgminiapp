from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Size(Base):
    __tablename__ = "sizes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(64), nullable=False)

    # clothes, shoes, accessory
    type: Mapped[str] = mapped_column(String(64), nullable=False)

    products: Mapped[list["Product"]] = relationship(
        back_populates="size",
    )
