from fastapi import APIRouter, Depends, Query, status, Response

from app.deps import get_current_user_id, get_info_api_client, get_commissions_service, get_payouts_service
from app.services.calculation import CalculationService
from app.schemas import CalculationRequest, CalculationChooseOffer, PayOffer
from app.deps import get_agent_service
from app.services.agents import AgentService
from app.services.commission import CommissionService
from app.services.payouts import PayoutService
from app.schemas import AgentCreate, AgentRead, AgentUpdate
from app.clients.info_api import InfoAPIClient

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.get("/me", response_model=AgentRead)
async def me(
    user_id: int = Depends(get_current_user_id),
    service: AgentService = Depends(get_agent_service),
):
    agent = await service.me(agent_id=user_id)
    return agent

@router.patch("/", response_model=AgentRead)
async def update(
    data:AgentUpdate,
    user_id: int = Depends(get_current_user_id),
    service: AgentService = Depends(get_agent_service),
):
    agent = await service.update(agent_id=user_id, data=data)
    return agent

@router.get("/calculations")
async def get_calculations(
    user_id: int = Depends(get_current_user_id),
    service: AgentService = Depends(get_agent_service),
    info_api: InfoAPIClient = Depends(get_info_api_client)
):
    result = await service.get_calculations(agent_id=user_id, info_api=info_api)
    return result


@router.get("/commissions")
async def get_commissions(
    user_id: int = Depends(get_current_user_id),
    service: CommissionService = Depends(get_commissions_service),
):
    result = await service.get_commissions(agent_id=user_id)
    return result

@router.get("/payouts")
async def get_payouts(
    user_id: int = Depends(get_current_user_id),
    service: PayoutService = Depends(get_payouts_service),
):
    result = await service.get_payouts(agent_id=user_id)
    return result

@router.post("/payouts")
async def create_payout(
    user_id: int = Depends(get_current_user_id),
    service: PayoutService = Depends(get_payouts_service),
):
    result = await service.create_payout(agent_id=user_id)
    return result