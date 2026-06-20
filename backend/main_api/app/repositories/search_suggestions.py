from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.search_suggestions import SearchSuggestion
from app.repositories.base import BaseRepository
from app.schemas.search_suggestions import (
    SearchSuggestionCreateRepository,
    SearchSuggestionUpdate,
)


class SearchSuggestionRepository(
    BaseRepository[
        SearchSuggestion,
        SearchSuggestionCreateRepository,
        SearchSuggestionUpdate,
    ]
):
    model = SearchSuggestion

    async def register_query(self, query: str) -> SearchSuggestion:
        cleaned_query = " ".join(query.split())
        normalized_query = cleaned_query.casefold()
        stmt = insert(SearchSuggestion).values(
            query=cleaned_query,
            normalized_query=normalized_query,
            popularity=1,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[SearchSuggestion.normalized_query],
            set_={"popularity": SearchSuggestion.popularity + 1},
        ).returning(SearchSuggestion)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def suggest(self, query: str, *, limit: int = 10) -> list[SearchSuggestion]:
        normalized_query = " ".join(query.split()).casefold()
        stmt = (
            select(SearchSuggestion)
            .where(SearchSuggestion.normalized_query.startswith(normalized_query))
            .order_by(SearchSuggestion.popularity.desc(), SearchSuggestion.query)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
