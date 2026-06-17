from app.db.uow import UnitOfWork
from fastapi.exceptions import HTTPException
from fastapi import status
class BaseService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def check_agent_status(self, agent_id: int) -> bool:
        async with self.uow as uow:
            agent = await uow.agents.read(id=agent_id)

            if agent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found",
                )

            if agent.status == "individual":
                return False

            return True