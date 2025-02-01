
from pydantic import BaseModel

class ChatRequestBody(BaseModel):
    message: str

class ChatBodyResponse(BaseModel):
    result: str
    
    