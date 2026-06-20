from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.users import User
from app.repositories.base import BaseRepository
from app.schemas.telegram import TelegramWebAppUser
from app.schemas.users import UserCreateRepository, UserUpdate


class UserRepository(BaseRepository[User, UserCreateRepository, UserUpdate]):
    model = User

    async def read_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_from_telegram(self, telegram_user: TelegramWebAppUser) -> User:
        data = UserCreateRepository.from_telegram(telegram_user).model_dump()
        stmt = insert(User).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[User.telegram_id],
            set_={
                "username": stmt.excluded.username,
            },
        ).returning(User)
        result = await self.session.execute(stmt)
        return result.scalar_one()
