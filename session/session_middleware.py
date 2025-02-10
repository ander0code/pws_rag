import logging
from fastapi import Request
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
        
        # user_id = request.headers.get("Authorization")
        # if not user_id:
        #     logger.warning("Unauthorized access attempt: Missing user ID")
        #     raise HTTPException(status_code=401, detail="Unauthorized")
        
        # request.state.user_id = user_id
        
        logger.info("User is authorized")
        return await call_next(request)


async def get_session(request: Request):
    return request.state.user_id