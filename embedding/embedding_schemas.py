from pydantic import BaseModel

class EmbeddingMetadata(BaseModel):
    companyId: int
    source: str

class EmbeddingCreateRequest(BaseModel):
    content: str
    source: str

class EmbeddingCreateResponse(BaseModel):
    
    success: bool
    #success: bool = Field(..., example=True)