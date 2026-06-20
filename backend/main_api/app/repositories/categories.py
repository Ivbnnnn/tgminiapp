from sqlalchemy import select

from app.models.categories import Category
from app.repositories.base import BaseRepository
from app.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    model = Category

    async def read_children(self, parent_id: int | None = None) -> list[Category]:
        condition = Category.parent_id.is_(None) if parent_id is None else Category.parent_id == parent_id
        stmt = select(Category).where(condition).order_by(Category.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
