from sqlalchemy import select

from app.models.sizes import Size
from app.repositories.base import BaseRepository
from app.schemas.sizes import SizeCreate, SizeType, SizeUpdate


class SizeRepository(BaseRepository[Size, SizeCreate, SizeUpdate]):
    model = Size

    async def read_by_type(self, size_type: SizeType) -> list[Size]:
        stmt = select(Size).where(Size.type == size_type).order_by(Size.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
