from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PayoutBase(BaseModel):
    agent_id: int
    total_amount: Decimal



class PayoutCreate(PayoutBase):
    pass


class PayoutUpdate(BaseModel):
    total_amount: Decimal | None = None
    


class PayoutRead(PayoutBase):
    id: int
    paid_at: datetime 

    model_config = ConfigDict(from_attributes=True)