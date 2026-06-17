from app.services.base import BaseService
from app.schemas import CalculationRequest, CalculationCreate, CalculationCompanyCreate, CommissionCreate
from app.clients.info_api import InfoAPIClient
from fastapi.exceptions import HTTPException
from fastapi import status
from app.utils.calculation import make_policy_price_list
from app.core.config import settings
from app.core.logger import logger
from decimal import Decimal


class CalculationService(BaseService):
    async def make_offers(self, data:CalculationRequest, info_api:InfoAPIClient, agent_id:int):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            info_api_result = await info_api.get_info_for_calculation(data.model_dump())
            logger.info(info_api_result)
            
            result = make_policy_price_list(
                driver=info_api_result["driver"][0],
                companies=info_api_result["companies"],
                vehicle_and_sts=info_api_result["vehicle_and_sts"][0],
                person_and_address=info_api_result["person_and_address"][0],
                use_period=data.use_period,
                BASE_PRICE=settings.BASE_PRICE
            )
            payload = CalculationCreate(
                agent_id=agent_id,
                driver_id=info_api_result["driver"][0]["id"],
                vehicle_id=info_api_result["vehicle_and_sts"][0]["id"],
                owner_id=info_api_result["person_and_address"][0]["id"],
                policy_start_date=data.policy_start_date,
                use_period=data.use_period,
                status="calculated"
            )
            calculation_db = await uow.calculations.insert(
                data=payload
            )
            for offer in result:
                db_row = CalculationCompanyCreate(
                    agent_id=agent_id,
                    insurance_company_id=offer["id"],
                    policy_price=offer["policy_price"],
                    calculation_id = calculation_db.id
                )
                await uow.calculations_companies.insert(db_row)
        return {
                "offers":result,
                "calculation_id":calculation_db.id
                }
            #вызываю эту функцию
            
            #делаю запись в бд status calculated
            #после юзается другой роут и другая функция этого класса, где выбирается конкретная компания (после оплаты полиса)

            #вызвать репозиторий коммиссий чтобы создать запись коммиссии со статусом черновик (не оплачен полис)
            #после оплаты полиса в сервисе комиссий вызывать метод который будет менять этот статус (запрос на роут - типа оплата)

        
    async def choose_offer(self, agent_id:int, company_id:int, calculation_id:int):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            calculation_company = await uow.calculations_companies.read_by_fields({
                "calculation_id":calculation_id,
                "insurance_company_id":company_id,
                "agent_id":agent_id
            })
            calculation = await uow.calculations.read(id = calculation_company.calculation_id)

            if calculation.status == "paid":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Calculation is already paid",
                )

            if calculation.status not in {"calculated", "waiting_for_payment"}:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Calculation cannot be changed in current status",
                )

            calculation.policy_price = calculation_company.policy_price
            calculation.insurance_company_id = calculation_company.insurance_company_id
            calculation.status = "waiting_for_payment"

        return {"status":"ok"}
    

    async def pay_offer(self, agent_id:int, calculation_id:int, info_api:InfoAPIClient,):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            calculation = await uow.calculations.read_by_fields({
                "id":calculation_id,
                "agent_id":agent_id
            })

            if calculation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Calculation not found",
                )

            if calculation.status == "paid":
                existing_commission = await uow.commissions.read_by_fields({
                    "agent_id":agent_id,
                    "calculation_id":calculation_id,
                })
                return {
                    "status":"already_paid",
                    "commission": existing_commission,
                }

            if calculation.status != "waiting_for_payment":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Choose an offer before payment",
                )

            if calculation.insurance_company_id is None or calculation.policy_price is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Calculation has no selected offer",
                )

            existing_commission = await uow.commissions.read_by_fields({
                "agent_id":agent_id,
                "calculation_id":calculation_id,
            })

            if existing_commission is not None:
                calculation.status="paid"
                return {
                    "status":"already_paid",
                    "commission": existing_commission,
                }

            calculation.status="paid"

            #получить amount
            percent = await info_api.get_company_percent(
                insurance_company_id=calculation.insurance_company_id
            )
            com_payload = CommissionCreate(
                agent_id=agent_id,
                insurance_company_id=calculation.insurance_company_id,
                calculation_id=calculation.id,
                policy_price=calculation.policy_price,
                amount=calculation.policy_price * percent / 100,      
                percent= percent,
                status = "waiting_for_payout"          
            )
            commission = await uow.commissions.insert(com_payload)

        return {"status":"ok", "commission": commission}
    

    async def get_insurance_companies(self, info_api:InfoAPIClient,):
        result = await info_api.get_all_insurance_companies()
        return result
    

    async def cancel_offers(self, agent_id:int, company_id:int, calculation_id:int):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            calculation_company = await uow.calculations_companies.read_by_fields({
                "calculation_id":calculation_id,
                "insurance_company_id":company_id,
                "agent_id":agent_id
            })
            calculation = await uow.calculations.read(id = calculation_company.calculation_id)
            if calculation.status == "waiting_for_payout":
                calculation.status = "canceled"
            else:
                return {"wrong calculation status"}

        return {"status":"ok"}
