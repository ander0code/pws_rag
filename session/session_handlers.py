import uuid
from session.session_service import SessionService
from session.session_schemas import SessionRequestBody, UserSession
import logging
logger = logging.getLogger("uvicorn")

session_service = SessionService()

async def create(body: SessionRequestBody) -> UserSession:
    try:
        logger.info(f"Creando sesión para userId: {body.userId} y companyId: {body.companyId}")

        chat_session_id = str(uuid.uuid4())
        logger.debug(f"Generado ChatSessionId: {chat_session_id}")
        user_session = UserSession(
            userId=body.userId,
            companyId=body.companyId,
            ChatSessionId=chat_session_id
        )
        logger.debug(f"UserSession creado: {user_session}")

        await session_service.create_session(user_session)
        logger.info(f"Sesión creada con ChatSessionId: {chat_session_id}")
        return user_session
    except Exception as e:
        logger.error(f"Error en create: {e}")
        raise e