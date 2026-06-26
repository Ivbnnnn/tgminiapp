from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.telegram import TelegramWebAppUser


class UserCreateRepository(BaseModel):
    telegram_id: int = Field(gt=0)
    username: str | None = Field(default=None, max_length=255)

    @classmethod
    def from_telegram(cls, user: TelegramWebAppUser) -> "UserCreateRepository":
        return cls(
            telegram_id=user.id,
            username=user.username,
        )


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=255)


class UserRead(ORMModel):
    id: int
    telegram_id: int
    username: str | None
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime
