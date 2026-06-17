from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CommissionBase(BaseModel):
    agent_id: int
    insurance_company_id: int
    calculation_id: int

    policy_price: Decimal
    percent: Decimal
    amount: Decimal

    status: str
    paid_at: datetime | None = None


class CommissionCreate(CommissionBase):
    pass


class CommissionUpdate(BaseModel):
    insurance_company_id: int | None = None
    calculation_id: int | None = None

    policy_price: Decimal | None = None
    percent: Decimal | None = None
    amount: Decimal | None = None

    status: str | None = None
    paid_at: datetime | None = None


class CommissionRead(CommissionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)