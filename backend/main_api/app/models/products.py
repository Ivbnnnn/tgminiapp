from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    category_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
    )
    size_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("sizes.id", ondelete="SET NULL"),
        nullable=True,
    )
    seller_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("sellers.id", ondelete="SET NULL"),
        nullable=True,
    )

    seller_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    seller_telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # new, used, vintage, damaged
    condition: Mapped[str] = mapped_column(String(64), nullable=False, default="used")

    # male, female, unisex, kids
    gender: Mapped[Optional[str]] = mapped_column(String(64))

    color: Mapped[Optional[str]] = mapped_column(String(64))
    material: Mapped[Optional[str]] = mapped_column(String(128))

    is_unique: Mapped[bool] = mapped_column(nullable=False, default=True)

    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # active, reserved, sold, hidden, deleted
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="active")

    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped[Optional["Category"]] = relationship(
        back_populates="products",
    )
    brand: Mapped[Optional["Brand"]] = relationship(
        back_populates="products",
    )
    size: Mapped[Optional["Size"]] = relationship(
        back_populates="products",
    )
    seller: Mapped[Optional["Seller"]] = relationship(
        back_populates="products",
    )

    photos: Mapped[list["ProductPhoto"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductPhoto.position",
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["UserEvent"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        CheckConstraint("stock_quantity >= 0", name="ck_products_stock_non_negative"),
        Index("idx_products_category_id", "category_id"),
        Index("idx_products_brand_id", "brand_id"),
        Index("idx_products_size_id", "size_id"),
        Index("idx_products_seller_id", "seller_id"),
        Index("idx_products_status", "status"),
        Index("idx_products_price", "price"),
        Index("idx_products_search_vector", "search_vector", postgresql_using="gin"),
    )
