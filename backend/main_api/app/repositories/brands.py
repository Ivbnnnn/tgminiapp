from sqlalchemy import select

from app.models.brands import Brand
from app.repositories.base import BaseRepository
from app.schemas.brands import BrandCreateRepository, BrandUpdate, BrandUpdateRepository


class BrandRepository(BaseRepository[Brand, BrandCreateRepository, BrandUpdateRepository]):
    model = Brand

    async def create(self, name: str) -> Brand | None:
        cleaned_name = " ".join(name.split())
        return await self.insert(
            BrandCreateRepository(
                name=cleaned_name,
                normalized_name=cleaned_name.casefold(),
            )
        )

    async def update_brand(self, brand_id: int, data: BrandUpdate) -> Brand | None:
        if data.name is None:
            return await self.read(brand_id)
        cleaned_name = " ".join(data.name.split())
        return await self.update(
            brand_id,
            BrandUpdateRepository(
                name=cleaned_name,
                normalized_name=cleaned_name.casefold(),
            ),
        )

    async def search(self, query: str, *, limit: int = 20) -> list[Brand]:
        stmt = (
            select(Brand)
            .where(Brand.name.ilike(f"%{query.strip()}%"))
            .order_by(Brand.name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
