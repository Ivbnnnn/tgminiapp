import pytest
from fastapi import HTTPException

from app.deps import get_current_seller
from app.models.sellers import Seller
from app.models.users import User


class SellerLookup:
    def __init__(self, seller: Seller | None):
        self.seller = seller

    async def read_by_telegram_id(self, telegram_id: int) -> Seller | None:
        assert telegram_id == 123456
        return self.seller


class FakeUow:
    def __init__(self, seller: Seller | None):
        self.sellers = SellerLookup(seller)


@pytest.mark.asyncio
async def test_regular_user_cannot_publish() -> None:
    user = User(id=1, telegram_id=123456, username="buyer")
    with pytest.raises(HTTPException) as error:
        await get_current_seller(user=user, uow=FakeUow(None))  # type: ignore[arg-type]
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_active_seller_can_publish() -> None:
    user = User(id=1, telegram_id=123456, username="seller")
    seller = Seller(id=2, telegram_id=123456, user_id=1, is_active=True)
    result = await get_current_seller(user=user, uow=FakeUow(seller))  # type: ignore[arg-type]
    assert result.id == 2
