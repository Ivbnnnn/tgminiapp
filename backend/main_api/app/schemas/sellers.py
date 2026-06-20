from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SellerCreate(BaseModel):
    telegram_id: int = Field(gt=0)
    display_name: str | None = Field(default=None, max_length=255)


class SellerUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class SellerRead(ORMModel):
    id: int
    user_id: int | None
    telegram_id: int
    username: str | None
    display_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
