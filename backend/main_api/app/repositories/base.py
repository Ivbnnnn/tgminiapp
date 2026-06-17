from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(
        self,
        data: CreateSchemaType | dict[str, Any],
    ) -> ModelType | None:
        values = self._to_dict(data)

        stmt = (
            insert(self.model)
            .values(**values)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def read(
        self,
        id: int,
    ) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def read_all(
        self,
        id: int,
    ) -> list[ModelType] | None:
        stmt = select(self.model).where(self.model.id == id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_fields(
        self,
        fields: dict[str, Any],
    ) -> ModelType | None:
        stmt = select(self.model)

        for field_name, value in fields.items():
            column = getattr(self.model, field_name, None)

            if column is None:
                raise ValueError(
                    f"Field '{field_name}' not found in model {self.model.__name__}"
                )

            stmt = stmt.where(column == value)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def read_by_fields_all(
        self,
        fields: dict[str, Any],
    ) -> list[ModelType]:
        stmt = select(self.model)

        for field_name, value in fields.items():
            column = getattr(self.model, field_name, None)

            if column is None:
                raise ValueError(
                    f"Field '{field_name}' not found in model {self.model.__name__}"
                )

            stmt = stmt.where(column == value)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        id: int,
        data: UpdateSchemaType | dict[str, Any],
    ) -> ModelType | None:
        values = self._to_dict(data, exclude_none=True)

        if not values:
            return await self.read(id)

        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**values)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(
        self,
        id: int,
    ) -> ModelType | None:
        stmt = (
            delete(self.model)
            .where(self.model.id == id)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _to_dict(
        self,
        data: BaseModel | dict[str, Any],
        exclude_none: bool = False,
    ) -> dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_none=exclude_none)

        if exclude_none:
            return {
                key: value
                for key, value in data.items()
                if value is not None
            }

        return data