from fastapi import HTTPException, status
from embedding.embedding_service import EmbeddingService
from embedding.embedding_repository import QdrantEmbeddingRepository
import logging
logger = logging.getLogger("uvicorn")


embedding_repository = QdrantEmbeddingRepository()

embedding_service = EmbeddingService(repository=embedding_repository)


def create_embedding_logic(request: dict):
    content = request.get("content")
    source = request.get("source")
    company_id = request.get("company_id")
    user_id = request.get("user_id") 

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id es requerido"
        )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id es requerido"
        )

    success = embedding_service.save_embedding(
        content,
        {
            "companyId": int(company_id),
            "userId": int(user_id),
            "source": source
        }
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al guardar el embedding"
        )
    return success