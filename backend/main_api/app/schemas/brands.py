from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class BrandBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class BrandCreate(BrandBase):
    pass


class BrandCreateRepository(BrandBase):
    normalized_name: str = Field(min_length=1, max_length=255)


class BrandUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class BrandUpdateRepository(BrandUpdate):
    normalized_name: str | None = Field(default=None, min_length=1, max_length=255)


class BrandRead(BrandBase, ORMModel):
    id: int
    normalized_name: str
