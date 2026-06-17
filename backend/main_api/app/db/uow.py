from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.agents_repository import AgentRepository
from app.repositories.calculation_repostitory import CalculationRepository
from app.repositories.commission_repository import CommissionRepository
from app.repositories.calculation_companies import CalculationCompaniesRepository
from app.repositories.payout_commissions_repository import PayoutCommissionRepository
from app.repositories.payouts_repository import PayoutRepository
class UnitOfWork():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session=session)
        self.calculations = CalculationRepository(session=session)
        self.commissions = CommissionRepository(session=session)
        self.calculations_companies = CalculationCompaniesRepository(session=session)
        self.payout_commissions = PayoutCommissionRepository(session=session)
        self.payouts = PayoutRepository(session=session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
            
    async def commit(self):
        await self.session.commit()
    async def rollback(self):
        await self.session.rollback()
