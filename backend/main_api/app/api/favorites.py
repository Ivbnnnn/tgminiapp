from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.db.uow import UnitOfWork
from app.deps import get_current_user, get_uow
from app.models.users import User
from app.schemas.favorites import FavoriteCreate
from app.schemas.products import ProductDetail


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("", response_model=list[ProductDetail])
async def list_favorites(
    user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    return await uow.favorites.read_products(user.id)


@router.get("/{product_id}")
async def favorite_status(
    product_id: int,
    user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> dict[str, bool]:
    return {"is_favorite": await uow.favorites.contains(user.id, product_id)}


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def add_favorite(
    data: FavoriteCreate,
    user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> Response:
    if await uow.products.read(data.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await uow.favorites.add(user.id, data.product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    product_id: int,
    user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> Response:
    await uow.favorites.remove(user.id, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
