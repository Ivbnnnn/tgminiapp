from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class FavoriteCreate(BaseModel):
    """User id is derived from the authenticated Telegram session."""

    product_id: int = Field(gt=0)


class FavoriteCreateRepository(FavoriteCreate):
    user_id: int = Field(gt=0)


class FavoriteRead(FavoriteCreateRepository, ORMModel):
    created_at: datetime
