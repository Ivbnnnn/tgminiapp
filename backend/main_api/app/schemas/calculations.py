from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CalculationBase(BaseModel):
    agent_id: int

    insurance_company_id: int | None = None
    driver_id: int
    vehicle_id: int
    owner_id: int

    policy_price: Decimal | None = None
    status: str

    policy_start_date: date
    use_period: int


class CalculationCreate(CalculationBase):
    pass


class CalculationChooseOffer(BaseModel):
    company_id:int
    calculation_id:int


class PayOffer(BaseModel):
    calculation_id:int


class CalculationUpdate(BaseModel):
    insurance_company_id: int | None = None
    driver_id: int | None = None
    vehicle_id: int | None = None
    owner_id: int | None = None

    policy_price: Decimal | None = None
    status: str | None = None

    policy_start_date: date | None = None
    use_period: int | None = None


class CalculationRead(CalculationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchFilter(BaseModel):
    field: str
    value: str


class SearchRequest(BaseModel):
    model_name:str
    relations:list[str]
    filters:list[SearchFilter] | dict[str, str]
    
class CalculationRequest(BaseModel):
    lastname: str
    firstname: str
    middlename: str | None = None
    insurance_companies: list[str] | None = None
    license_plate:str | None = None
    vin:str | None = None
    body_number:str | None = None
    chassis_number:str | None = None
    license_serial:str | None = None
    license_number:str | None = None
    use_period:int
    policy_start_date:date


class CalculationTestData(CalculationRequest):
    pass
