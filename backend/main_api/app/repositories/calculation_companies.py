from app.repositories.base import BaseRepository
from sqlalchemy import insert, select
from app.models.calculation_companies import CalculationCompanies
from app.schemas.calculation_companies import CalculationCompanyCreate
class CalculationCompaniesRepository(BaseRepository[CalculationCompanies, CalculationCompanyCreate, CalculationCompanyCreate]):
    model = CalculationCompanies
