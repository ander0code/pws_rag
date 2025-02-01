import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from session.session_repository import RedisSessionRepository
from session.session_service import SessionService

logger = logging.getLogger("uvicorn")
session_service = SessionService(RedisSessionRepository())

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip('/')
        method = request.method
        
        logger.info(f"Request path: {path}, method: {method}")
        
        if path == "/session" and method == "POST":
            return await call_next(request)
        
        session_id = request.headers.get("Authorization")
        if not session_id:
            logger.warning("Unauthorized access attempt: Missing Authorization header")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        session = await session_service.get_session(session_id)
        if not session:
            logger.warning("Unauthorized access attempt: Invalid session ID")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        request.state.session = session
        request.state.session_id = session_id
        
        logger.info("Session is authorized")
        return await call_next(request)

async def get_session(request: Request):
    return request.state.session