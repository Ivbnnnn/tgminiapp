from sqlalchemy import select

from app.models.user_events import UserEvent
from app.repositories.base import BaseRepository
from app.schemas.user_events import UserEventCreateRepository


class UserEventRepository(
    BaseRepository[UserEvent, UserEventCreateRepository, UserEventCreateRepository]
):
    model = UserEvent

    async def read_recent(
        self,
        *,
        user_id: int | None = None,
        product_id: int | None = None,
        limit: int = 100,
    ) -> list[UserEvent]:
        stmt = select(UserEvent)
        if user_id is not None:
            stmt = stmt.where(UserEvent.user_id == user_id)
        if product_id is not None:
            stmt = stmt.where(UserEvent.product_id == product_id)
        stmt = stmt.order_by(UserEvent.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
