import redis.asyncio as redis
import uuid
from session.session_schemas import UserSession
from session.session_interface import ISessionRepository
from config.config import app_env
from dotenv import load_dotenv
import logging

logger = logging.getLogger("uvicorn")

load_dotenv()
env_settings = app_env


class RedisSessionRepository(ISessionRepository):
    def __init__(self, redis_url: str = env_settings.REDIS_URL):
        self.redis = redis.from_url(redis_url)
        logger.info(f"Conectado a Redis en {redis_url}")

    async def create_session(self, session: UserSession) -> str:
        try:
            if not session.ChatSessionId:
                session.ChatSessionId = str(uuid.uuid4())
            session_data = session.model_dump_json()
            await self.redis.set(session.ChatSessionId, session_data, ex=env_settings.REDIS_SESSION_TTL)  # Expira en 1 hora
            logger.info(f"Session creada: {session.ChatSessionId}")
            return session.ChatSessionId
        except Exception as e:
            logger.error(f"Error creando sesión: {e}")
            raise e

    async def get_session(self, session_id: str) -> UserSession | None:
        try:
            session_data = await self.redis.get(session_id)
            if session_data:
                logger.info(f"Session encontrada: {session_id}")
                return UserSession.model_validate_json(session_data)
            logger.warning(f"Session no encontrada: {session_id}")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo sesión: {e}")
            raise e

    async def delete_session(self, session_id: str) -> bool:
        try:
            result = await self.redis.delete(session_id)
            if result == 1:
                logger.info(f"Session eliminada: {session_id}")
                return True
            logger.warning(f"No se pudo eliminar la session: {session_id}")
            return False
        except Exception as e:
            logger.error(f"Error eliminando sesión: {e}")
            raise e