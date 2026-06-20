from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class SearchSuggestionCreate(BaseModel):
    query: str = Field(min_length=1, max_length=255)

    @field_validator("query")
    @classmethod
    def normalize_whitespace(cls, value: str) -> str:
        return " ".join(value.split())


class SearchSuggestionCreateRepository(SearchSuggestionCreate):
    normalized_query: str = Field(min_length=1, max_length=255)
    popularity: int = Field(default=1, ge=0)


class SearchSuggestionUpdate(BaseModel):
    query: str | None = Field(default=None, min_length=1, max_length=255)
    normalized_query: str | None = Field(default=None, min_length=1, max_length=255)
    popularity: int | None = Field(default=None, ge=0)


class SearchSuggestionRead(SearchSuggestionCreateRepository, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
