from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.uow import UnitOfWork
from app.models.users import User
from app.models.sellers import Seller
from app.core.config import settings


async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[UnitOfWork, None]:
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise


def get_current_user_id(request: Request) -> int:
    return request.state.user_id


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    uow: UnitOfWork = Depends(get_uow),
) -> User:
    user = await uow.users.read(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_seller(
    user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> Seller:
    seller = await uow.sellers.read_by_telegram_id(user.telegram_id)
    if seller is None or not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Publishing is available only to approved sellers",
        )
    return seller


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.telegram_id not in settings.admin_telegram_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
