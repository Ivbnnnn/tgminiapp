from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.favorites import Favorite
from app.models.products import Product


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int, product_id: int) -> Favorite | None:
        stmt = (
            insert(Favorite)
            .values(user_id=user_id, product_id=product_id)
            .on_conflict_do_nothing(
                index_elements=[Favorite.user_id, Favorite.product_id]
            )
            .returning(Favorite)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def remove(self, user_id: int, product_id: int) -> bool:
        stmt = delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id,
        )
        result = await self.session.execute(stmt)
        return bool(result.rowcount)

    async def contains(self, user_id: int, product_id: int) -> bool:
        stmt = select(
            exists().where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id,
            )
        )
        return bool(await self.session.scalar(stmt))

    async def read_products(
        self,
        user_id: int,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        stmt = (
            select(Product)
            .join(Favorite, Favorite.product_id == Product.id)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.brand),
                selectinload(Product.size),
                selectinload(Product.photos),
            )
            .order_by(Favorite.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
