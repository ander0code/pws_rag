from .session_interface import ISessionService
from .session_repository import RedisSessionRepository
from .session_schemas import UserSession
from typing import Optional
import logging

logger = logging.getLogger("uvicorn")

class SessionService(ISessionService):
    def __init__(self, repository: RedisSessionRepository = None):
        if repository is None:
            self.repository = RedisSessionRepository()
            logger.info("RedisSessionRepository iniciada por defecto en SessionService.")
        else:
            self.repository = repository
            logger.info("RedisSessionRepository proporcionada en SessionService.")


    async def create_session(self, session: UserSession) -> str:
        logger.debug(f"Creating session: {session}")
        return await self.repository.create_session(session)

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        logger.debug(f"Getting session for session_id: {session_id}")
        return await self.repository.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        logger.debug(f"Deleting session for session_id: {session_id}")
        return await self.repository.delete_session(session_id)