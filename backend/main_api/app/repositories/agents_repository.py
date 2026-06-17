from app.repositories.base import BaseRepository
from sqlalchemy import insert, select
from backend.main_api.app.models.users import Agent
from app.schemas.agents import AgentCreateRepository, AgentUpdate
class AgentRepository(BaseRepository[Agent, AgentCreateRepository, AgentUpdate]):
    model = Agent
