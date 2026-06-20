from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


SizeType = Literal["clothes", "shoes", "accessory"]


class SizeBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    type: SizeType


class SizeCreate(SizeBase):
    pass


class SizeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    type: SizeType | None = None


class SizeRead(SizeBase, ORMModel):
    id: int
