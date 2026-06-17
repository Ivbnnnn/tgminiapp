from pydantic import BaseModel, ConfigDict


class PayoutCommissionBase(BaseModel):
    payout_id: int
    commission_id: int


class PayoutCommissionCreate(PayoutCommissionBase):
    pass


class PayoutCommissionRead(PayoutCommissionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)