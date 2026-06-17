from app.repositories.base import BaseRepository
from sqlalchemy import insert, select
from app.models.calculations import Calculation
from app.schemas.calculations import CalculationCreate, CalculationUpdate
class CalculationRepository(BaseRepository[Calculation, CalculationCreate, CalculationUpdate]):
    model = Calculation

