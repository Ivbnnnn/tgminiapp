from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.db.uow import UnitOfWork
from app.deps import get_uow
from app.schemas.brands import BrandCreate, BrandRead, BrandUpdate
from app.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.sizes import SizeCreate, SizeRead, SizeUpdate


router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/brands", response_model=list[BrandRead])
async def list_brands(uow: UnitOfWork = Depends(get_uow)):
    return await uow.brands.read_all()


@router.post("/brands", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
async def create_brand(data: BrandCreate, uow: UnitOfWork = Depends(get_uow)):
    return await uow.brands.create(data.name)


@router.patch("/brands/{item_id}", response_model=BrandRead)
async def update_brand(item_id: int, data: BrandUpdate, uow: UnitOfWork = Depends(get_uow)):
    item = await uow.brands.update_brand(item_id, data)
    return _found(item)


@router.delete("/brands/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(item_id: int, uow: UnitOfWork = Depends(get_uow)) -> Response:
    _found(await uow.brands.delete(item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(parent_id: int | None = None, uow: UnitOfWork = Depends(get_uow)):
    return await uow.categories.read_children(parent_id)


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, uow: UnitOfWork = Depends(get_uow)):
    return await uow.categories.insert(data)


@router.patch("/categories/{item_id}", response_model=CategoryRead)
async def update_category(item_id: int, data: CategoryUpdate, uow: UnitOfWork = Depends(get_uow)):
    return _found(await uow.categories.update(item_id, data))


@router.delete("/categories/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(item_id: int, uow: UnitOfWork = Depends(get_uow)) -> Response:
    _found(await uow.categories.delete(item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sizes", response_model=list[SizeRead])
async def list_sizes(size_type: str | None = None, uow: UnitOfWork = Depends(get_uow)):
    if size_type is None:
        return await uow.sizes.read_all()
    if size_type not in {"clothes", "shoes", "accessory"}:
        raise HTTPException(status_code=422, detail="Unknown size type")
    return await uow.sizes.read_by_type(size_type)  # type: ignore[arg-type]


@router.post("/sizes", response_model=SizeRead, status_code=status.HTTP_201_CREATED)
async def create_size(data: SizeCreate, uow: UnitOfWork = Depends(get_uow)):
    return await uow.sizes.insert(data)


@router.patch("/sizes/{item_id}", response_model=SizeRead)
async def update_size(item_id: int, data: SizeUpdate, uow: UnitOfWork = Depends(get_uow)):
    return _found(await uow.sizes.update(item_id, data))


@router.delete("/sizes/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_size(item_id: int, uow: UnitOfWork = Depends(get_uow)) -> Response:
    _found(await uow.sizes.delete(item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _found(item: Any):
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
