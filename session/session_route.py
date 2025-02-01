from fastapi import APIRouter, Depends, HTTPException
from .session_schemas import SessionRequestBody, SessionCreateResponse
from .session_middleware import SessionMiddleware
from .session_handlers import create
from pydantic import ValidationError

session_router = APIRouter()

@session_router.post("/session", response_model=SessionCreateResponse, status_code=201)
async def create_session(body: SessionRequestBody):
    try:
        response = await create(body)
        return {"sessionId": response.ChatSessionId}
    
    except ValidationError:
        raise HTTPException(status_code=400, detail="Bad Request")
    except Exception as e:
        import logging
        logger = logging.getLogger("uvicorn")
        logger.error(f"Error en create_session: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@session_router.get("/protected", dependencies=[Depends(SessionMiddleware)])
async def protected_example():
    return {"message": "Authorized"}