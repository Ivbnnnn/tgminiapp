from sqlalchemy import delete, select

from app.models.product_photos import ProductPhoto
from app.repositories.base import BaseRepository
from app.schemas.product_photos import ProductPhotoCreate, ProductPhotoUpdate


class ProductPhotoRepository(
    BaseRepository[ProductPhoto, ProductPhotoCreate, ProductPhotoUpdate]
):
    model = ProductPhoto

    async def read_for_product(self, product_id: int) -> list[ProductPhoto]:
        stmt = (
            select(ProductPhoto)
            .where(ProductPhoto.product_id == product_id)
            .order_by(ProductPhoto.position)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_for_product(self, product_id: int) -> int:
        result = await self.session.execute(
            delete(ProductPhoto).where(ProductPhoto.product_id == product_id)
        )
        return result.rowcount or 0
