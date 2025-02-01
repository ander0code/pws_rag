from pydantic import BaseModel

class SessionRequestBody(BaseModel):
    userId: int
    companyId: int


class UserSession(BaseModel):
    userId: int
    companyId: int
    ChatSessionId: str

class SessionMiddlewareError(BaseModel):
    error: str

class SessionCreateResponse(BaseModel):
    sessionId: str
    
class EmbeddingCreateResponse(BaseModel):
    success: bool

