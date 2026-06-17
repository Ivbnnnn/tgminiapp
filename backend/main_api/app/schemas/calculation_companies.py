from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CalculationCompanyBase(BaseModel):
    agent_id: int
    insurance_company_id: int 
    policy_price: Decimal 
    calculation_id:int

class CalculationCompanyCreate(CalculationCompanyBase):
    pass
class CalculationCompanyRead(CalculationCompanyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
