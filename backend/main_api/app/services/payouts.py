from app.services.base import BaseService
from app.schemas import PayoutCommissionCreate, PayoutCreate
from app.clients.info_api import InfoAPIClient
from app.utils.calculation import make_policy_price_list
from app.core.config import settings
from fastapi.exceptions import HTTPException
from fastapi import status
from app.core.logger import logger
from decimal import Decimal
from datetime import datetime, timezone


class PayoutService(BaseService):
    async def create_payout(self,agent_id:int):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        #Достать комиссии в status = waiting_for_payout & agent_id = agent_id
        async with self.uow as uow:
            commissions = await uow.commissions.read_by_fields_all({
                "agent_id":agent_id,
                "status":"waiting_for_payout"
            })

            if not commissions:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No commissions available for payout",
                )

            total_amount = Decimal(0)

            for commission in commissions:
                total_amount += commission.amount
                commission.status='paid'
                commission.paid_at=datetime.now(timezone.utc)

            if total_amount <= Decimal(0):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Payout amount must be greater than zero",
                )

            p_data = PayoutCreate(
                agent_id=agent_id,
                total_amount=total_amount
            )
            payout = await uow.payouts.insert(p_data)
            for commission in commissions:
                p_c_data = PayoutCommissionCreate(
                    payout_id=payout.id,
                    commission_id=commission.id
                )
                await uow.payout_commissions.insert(p_c_data)
        return {"status":"ok"}
    
    async def get_payouts(self,agent_id:int):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            payouts = await uow.payouts.read_by_fields_all({
                "agent_id":agent_id
            })
        return payouts
