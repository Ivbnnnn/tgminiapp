from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.brands import BrandRead
from app.schemas.categories import CategoryRead
from app.schemas.common import ORMModel
from app.schemas.product_photos import ProductPhotoRead
from app.schemas.sizes import SizeRead


ProductCondition = Literal["new", "used", "vintage", "damaged"]
ProductGender = Literal["male", "female", "unisex", "kids"]
ProductStatus = Literal["active", "reserved", "sold", "hidden", "deleted"]
ProductModerationStatus = Literal["active", "hidden"]


class ProductBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10_000)
    category_id: int | None = Field(default=None, gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    size_id: int | None = Field(default=None, gt=0)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    condition: ProductCondition = "used"
    gender: ProductGender | None = None
    color: str | None = Field(default=None, max_length=64)
    material: str | None = Field(default=None, max_length=128)
    is_unique: bool = True
    stock_quantity: int = Field(default=1, ge=0)


class ProductCreate(ProductBase):
    """Public create DTO. Seller identity comes from validated Telegram initData."""

    pass


class ProductCreateRepository(ProductBase):
    seller_id: int = Field(gt=0)
    seller_telegram_id: int = Field(gt=0)
    seller_telegram_username: str | None = Field(default=None, max_length=255)
    status: ProductStatus | None = "active"


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10_000)
    category_id: int | None = Field(default=None, gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    size_id: int | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    condition: ProductCondition | None = None
    gender: ProductGender | None = None
    color: str | None = Field(default=None, max_length=64)
    material: str | None = Field(default=None, max_length=128)
    is_unique: bool | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    status: ProductStatus | None = None


class ProductModerationUpdate(BaseModel):
    status: ProductModerationStatus


class ProductRead(ProductBase, ORMModel):
    id: int
    seller_id: int | None
    seller_telegram_id: int
    seller_telegram_username: str | None
    status: ProductStatus
    created_at: datetime
    updated_at: datetime


class ProductDetail(ProductRead):
    category: CategoryRead | None = None
    brand: BrandRead | None = None
    size: SizeRead | None = None
    photos: list[ProductPhotoRead] = Field(default_factory=list)


class ProductFilters(BaseModel):
    query: str | None = Field(default=None, min_length=1, max_length=255)
    category_id: int | None = Field(default=None, gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    size_id: int | None = Field(default=None, gt=0)
    condition: ProductCondition | None = None
    gender: ProductGender | None = None
    status: ProductStatus = "active"
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    seller_telegram_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_price_range(self) -> "ProductFilters":
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("min_price cannot be greater than max_price")
        return self
