from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.models.products import Product
from app.repositories.base import BaseRepository
from app.schemas.products import (
    ProductCreate,
    ProductCreateRepository,
    ProductFilters,
    ProductUpdate,
)
from app.models.sellers import Seller


class ProductRepository(
    BaseRepository[Product, ProductCreateRepository, ProductUpdate]
):
    model = Product

    async def create_for_seller(
        self,
        data: ProductCreate,
        seller: Seller,
    ) -> Product:
        values = data.model_dump()
        product = await self.insert(
            ProductCreateRepository(
                **values,
                seller_id=seller.id,
                seller_telegram_id=seller.telegram_id,
                seller_telegram_username=seller.username,
            )
        )
        if product is None:
            raise RuntimeError("Could not create product")

        return product

    async def read_detail(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.brand),
                selectinload(Product.size),
                selectinload(Product.photos),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(
        self,
        filters: ProductFilters,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        stmt = select(Product).options(
            selectinload(Product.category),
            selectinload(Product.brand),
            selectinload(Product.size),
            selectinload(Product.photos),
        )

        for field in ("category_id", "brand_id", "size_id", "condition", "gender", "status", "seller_telegram_id"):
            value = getattr(filters, field)
            if value is not None:
                stmt = stmt.where(getattr(Product, field) == value)

        if filters.query:
            pattern = f"%{filters.query.strip()}%"
            stmt = stmt.where(
                or_(Product.title.ilike(pattern), Product.description.ilike(pattern))
            )
        if filters.min_price is not None:
            stmt = stmt.where(Product.price >= filters.min_price)
        if filters.max_price is not None:
            stmt = stmt.where(Product.price <= filters.max_price)

        stmt = stmt.order_by(Product.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
