from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.brands import BrandRepository
from app.repositories.categories import CategoryRepository
from app.repositories.favorites import FavoriteRepository
from app.repositories.product_photos import ProductPhotoRepository
from app.repositories.products import ProductRepository
from app.repositories.search_suggestions import SearchSuggestionRepository
from app.repositories.sizes import SizeRepository
from app.repositories.user_events import UserEventRepository
from app.repositories.users import UserRepository
from app.repositories.sellers import SellerRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.products = ProductRepository(session)
        self.product_photos = ProductPhotoRepository(session)
        self.categories = CategoryRepository(session)
        self.brands = BrandRepository(session)
        self.sizes = SizeRepository(session)
        self.favorites = FavoriteRepository(session)
        self.search_suggestions = SearchSuggestionRepository(session)
        self.user_events = UserEventRepository(session)
        self.sellers = SellerRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
