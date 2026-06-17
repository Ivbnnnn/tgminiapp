from app.services.base import BaseService
from app.schemas import CommissionUpdate, CommissionCreate
# from app.clients.info_api import InfoAPIClient
from app.utils.calculation import make_policy_price_list
from app.core.config import settings
from fastapi.exceptions import HTTPException
from fastapi import status
from app.core.logger import logger
from decimal import Decimal
class CommissionService(BaseService):
    async def get_commissions(self, agent_id:int):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            result = await uow.commissions.read_by_fields_all({
                "agent_id":agent_id
            })
            return result