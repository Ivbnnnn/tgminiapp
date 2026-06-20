from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.config import settings
from app.core.security import create_access_token, validate_telegram_init_data
from app.db.uow import UnitOfWork
from app.deps import get_uow
from app.schemas.telegram import TelegramAuthResponse, TelegramInitDataRequest


router = APIRouter(prefix="/auth", tags=["Auth"])


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

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="none" if settings.COOKIE_SECURE else "lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return TelegramAuthResponse(
        access_token=access_token,
        is_new_user=existing_user is None,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie("access_token")
