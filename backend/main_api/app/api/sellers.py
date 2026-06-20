from fastapi import APIRouter, Depends, HTTPException, status

from app.db.uow import UnitOfWork
from app.deps import get_current_admin, get_current_seller, get_uow
from app.models.sellers import Seller
from app.models.users import User
from app.schemas.sellers import SellerCreate, SellerRead, SellerUpdate


router = APIRouter(prefix="/sellers", tags=["Sellers"])


@router.get("/me", response_model=SellerRead)
async def read_seller_me(seller: Seller = Depends(get_current_seller)) -> Seller:
    return seller


@router.get("", response_model=list[SellerRead])
async def list_sellers(
    _: User = Depends(get_current_admin),
    uow: UnitOfWork = Depends(get_uow),
):
    return await uow.sellers.read_all()


@router.post("", response_model=SellerRead, status_code=status.HTTP_201_CREATED)
async def create_seller(
    data: SellerCreate,
    _: User = Depends(get_current_admin),
    uow: UnitOfWork = Depends(get_uow),
):
    existing = await uow.sellers.read_by_telegram_id(data.telegram_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Seller already exists")
    user = await uow.users.read_by_telegram_id(data.telegram_id)
    seller = await uow.sellers.insert(data)
    if seller is not None and user is not None:
        seller = await uow.sellers.link_user(user.telegram_id, user.id, user.username)
    return seller


@router.patch("/{seller_id}", response_model=SellerRead)
async def update_seller(
    seller_id: int,
    data: SellerUpdate,
    _: User = Depends(get_current_admin),
    uow: UnitOfWork = Depends(get_uow),
):
    seller = await uow.sellers.update(seller_id, data)
    if seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller
