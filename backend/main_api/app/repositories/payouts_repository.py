from app.repositories.base import BaseRepository
from sqlalchemy import insert, select
from app.models.payouts import Payout
from app.schemas import PayoutCreate, PayoutUpdate
class PayoutRepository(BaseRepository[Payout, PayoutCreate, PayoutUpdate]):
    model = Payout
