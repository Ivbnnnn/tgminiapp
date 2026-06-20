from sqlalchemy import select, update

from app.models.sellers import Seller
from app.repositories.base import BaseRepository
from app.schemas.sellers import SellerCreate, SellerUpdate


class SellerRepository(BaseRepository[Seller, SellerCreate, SellerUpdate]):
    model = Seller

    async def read_by_telegram_id(self, telegram_id: int) -> Seller | None:
        result = await self.session.execute(
            select(Seller).where(Seller.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def link_user(
        self,
        telegram_id: int,
        user_id: int,
        username: str | None,
    ) -> Seller | None:
        stmt = (
            update(Seller)
            .where(Seller.telegram_id == telegram_id)
            .values(user_id=user_id, username=username)
            .returning(Seller)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
