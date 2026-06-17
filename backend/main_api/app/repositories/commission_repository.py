from app.repositories.base import BaseRepository
from sqlalchemy import insert, select
from app.models.commissions import Commission
from app.schemas import CommissionCreate, CommissionUpdate
class CommissionRepository(BaseRepository[Commission, CommissionCreate, CommissionUpdate]):
    model = Commission
