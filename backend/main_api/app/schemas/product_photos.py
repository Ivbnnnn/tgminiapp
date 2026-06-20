from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProductPhotoInput(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    position: int = Field(ge=1, le=4)


class ProductPhotoCreate(ProductPhotoInput):
    product_id: int = Field(gt=0)


class ProductPhotoUpdate(BaseModel):
    url: str | None = Field(default=None, min_length=1, max_length=2048)
    position: int | None = Field(default=None, ge=1, le=4)


class ProductPhotoRead(ProductPhotoInput, ORMModel):
    id: int
    product_id: int
    created_at: datetime
