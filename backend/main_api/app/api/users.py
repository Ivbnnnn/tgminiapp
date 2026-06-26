from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models.users import User
from app.schemas.users import UserRead
from app.core.config import settings


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def read_me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user).model_copy(
        update={"is_admin": user.telegram_id in settings.admin_telegram_ids}
    )
