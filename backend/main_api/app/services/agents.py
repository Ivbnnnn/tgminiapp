from app.services.base import BaseService
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from app.clients.info_api import InfoAPIClient
from app.schemas import AgentCreate, AgentCreateRepository, AgentLogin, AgentUpdate
from app.utils.password import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token, decode_token
class AgentService(BaseService):
    async def signup(self, data: AgentCreate) -> dict[str, str]:
        async with self.uow:
            existing_agent = await self.uow.agents.read_by_fields(
                {
                    "email": data.email,
                }
            )

            if existing_agent is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Agent with this email already exists",
                )

            agent_data = data.model_dump()
            agent_data["password_hash"] = hash_password(
                agent_data.pop("password")
            )

            agent_create_data = AgentCreateRepository(**agent_data)

            try:
                agent = await self.uow.agents.insert(agent_create_data)
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Agent with this email already exists",
                )

            access_token = create_access_token(
                data={"sub": str(agent.id)}
            )

            refresh_token = create_refresh_token(
                data={"sub": str(agent.id)}
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    

    async def update(self, agent_id:int, data:AgentUpdate):
        async with self.uow:
            agent = await self.uow.agents.update(id = agent_id, data = data)
        return agent
    

    async def login(self, data: AgentLogin) -> dict[str, str]:
        async with self.uow:
            agent = await self.uow.agents.read_by_fields(
                {
                    "email": data.email,
                }
            )

            if agent is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            if not verify_password(data.password, agent.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            access_token = create_access_token(
                data={"sub": str(agent.id)}
            )

            refresh_token = create_refresh_token(
                data={"sub": str(agent.id)}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

    async def me(self, agent_id:int):
        async with self.uow as uow:
            agent = await uow.agents.read(id = agent_id)

        return agent
    

    async def refresh(self, refresh_token:str):
        async with self.uow as uow:
            payload = decode_token(refresh_token)
            agent_id = int(payload["sub"])
            agent = await uow.agents.read(id = agent_id)
            if agent == None:
                return "no"
            access_token = create_access_token(data = {"sub": str(agent.id)})
            return access_token
        

    async def get_calculations(self, agent_id:int, info_api:InfoAPIClient):
        can_create_calculation = await self.check_agent_status(agent_id=agent_id)

        if not can_create_calculation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Individual agents cannot create calculations",
            )
        async with self.uow as uow:
            calculations = await uow.calculations.read_by_fields_all({
                "agent_id":agent_id
            })
            result = []
            for row in calculations:
                driver = await info_api.get_driver_by_id(int(row.driver_id))
                vehicle = await info_api.get_vehicle_by_id(row.vehicle_id)
                owner = await info_api.get_owner_by_id(row.owner_id)
                if row.insurance_company_id != None:
                    company = await info_api.get_company_by_id(row.insurance_company_id)
                else:
                    company = None
                result.append({
                    "id":row.id,
                    "agent_id":row.agent_id,
                    "status":row.status,
                    "policy_start_date":row.policy_start_date,
                    "created_at": row.created_at,
                    "use_period":row.use_period,
                    "policy_price":row.policy_price,
                    "driver":driver,
                    "vehicle":vehicle,
                    "owner":owner,
                    "company":company
                })

            if calculations is [] or None:
                raise HTTPException(404, detail="calculations not found")
            return result
