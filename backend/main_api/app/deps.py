from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.clients.info_api import InfoAPIClient
from app.core.config import settings
from app.db.session import get_session
from app.db.uow import UnitOfWork
from app.services.agents import AgentService
from app.services.calculation import CalculationService
from app.services.commission import CommissionService
from app.services.payouts import PayoutService
import httpx

async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> UnitOfWork:
    return UnitOfWork(session)


def get_agent_service(
    uow: UnitOfWork = Depends(get_uow),
) -> AgentService:
    return AgentService(uow)


def get_calculation_service(
    uow: UnitOfWork = Depends(get_uow),
) -> CalculationService:
    return CalculationService(uow)


def get_commissions_service(
    uow: UnitOfWork = Depends(get_uow),
) -> CommissionService:
    return CommissionService(uow)

def get_payouts_service(
    uow: UnitOfWork = Depends(get_uow),
) -> PayoutService:
    return PayoutService(uow)


def get_current_user_id(request: Request) -> int:
    return request.state.user_id


async def get_info_api_client():
    async with httpx.AsyncClient(
        base_url=settings.INFO_API_URL,
        timeout=10.0,
    ) as client:
        yield InfoAPIClient(client)

