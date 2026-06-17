from app.repositories.base import BaseRepository
from sqlalchemy import insert, select
from app.models.payout_commissions import PayoutCommission
from app.schemas import PayoutCommissionCreate
class PayoutCommissionRepository(BaseRepository[PayoutCommission, PayoutCommissionCreate, PayoutCommissionCreate]):
    model = PayoutCommission
