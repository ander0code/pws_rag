
from abc import ABC, abstractmethod
from session.session_schemas import UserSession

class ISessionRepository(ABC):
    @abstractmethod
    async def create_session(self, session: UserSession) -> str:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> UserSession | None:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        pass

class ISessionService(ABC):
    @abstractmethod
    async def create_session(self, session: UserSession) -> str:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> UserSession | None:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        pass