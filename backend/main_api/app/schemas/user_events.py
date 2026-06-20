from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


UserEventType = Literal[
    "view",
    "like",
    "unlike",
    "add_to_cart",
    "remove_from_cart",
    "purchase",
    "search",
]


class UserEventCreate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    event_type: UserEventType
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    model_config = {"populate_by_name": True}


class UserEventCreateRepository(UserEventCreate):
    user_id: int | None = Field(default=None, gt=0)


class UserEventRead(UserEventCreateRepository, ORMModel):
    id: int
    created_at: datetime
