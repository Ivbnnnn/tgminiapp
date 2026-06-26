from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.config import settings
from app.core.security import create_access_token, validate_telegram_init_data
from app.db.uow import UnitOfWork
from app.deps import get_uow
from app.schemas.sellers import SellerCreate, SellerUpdate
from app.schemas.telegram import (
    DevAuthResponse,
    TelegramAuthResponse,
    TelegramInitDataRequest,
    TelegramWebAppUser,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


def set_access_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="none" if settings.COOKIE_SECURE else "lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/telegram", response_model=TelegramAuthResponse)
async def telegram_auth(
    data: TelegramInitDataRequest,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
) -> TelegramAuthResponse:
    try:
        validated_data = validate_telegram_init_data(data.init_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    existing_user = await uow.users.read_by_telegram_id(validated_data.user.id)
    user = await uow.users.upsert_from_telegram(validated_data.user)
    await uow.sellers.link_user(
        telegram_id=user.telegram_id,
        user_id=user.id,
        username=user.username,
    )
    access_token = create_access_token(user.id)

    set_access_cookie(response, access_token)
    return TelegramAuthResponse(
        access_token=access_token,
        is_new_user=existing_user is None,
    )


@router.post(
    "/dev",
    response_model=DevAuthResponse,
    include_in_schema=settings.DEV_MODE,
)
async def dev_auth(
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
) -> DevAuthResponse:
    if not settings.DEV_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    telegram_user = TelegramWebAppUser(
        id=settings.DEV_TELEGRAM_ID,
        first_name=settings.DEV_FIRST_NAME,
        username=settings.DEV_USERNAME,
        language_code="ru",
    )
    user = await uow.users.upsert_from_telegram(telegram_user)

    seller = await uow.sellers.read_by_telegram_id(user.telegram_id)
    if seller is None:
        seller = await uow.sellers.insert(
            SellerCreate(
                telegram_id=user.telegram_id,
                display_name=f"{settings.DEV_FIRST_NAME} (dev)",
            )
        )
    elif not seller.is_active:
        seller = await uow.sellers.update(
            seller.id,
            SellerUpdate(is_active=True),
        )
    if seller is not None:
        await uow.sellers.link_user(user.telegram_id, user.id, user.username)

    access_token = create_access_token(user.id)
    set_access_cookie(response, access_token)
    return DevAuthResponse(
        access_token=access_token,
        is_new_user=False,
        telegram_user=telegram_user,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie("access_token")
