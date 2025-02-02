# FILE: embedding_router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Annotated
from embedding.embedding_handler import create_embedding_logic
from embedding.embedding_schemas import EmbeddingCreateResponse
from session.session_middleware import get_session
from pydantic import ValidationError
from PyPDF2 import PdfReader
import io
import logging
logger = logging.getLogger("uvicorn")

embedding_route = APIRouter(
    prefix="/embedding",
    tags=["Embedding"],
)

@embedding_route.post(
    "/upload-pdf",
    response_model=EmbeddingCreateResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_pdf(
    company: Annotated[str, Depends(get_session)],
    file: UploadFile = File(...),
):
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)
        success = create_embedding_logic(
            {
                "content": text,
                "source": file.filename,
                "company_id": company,
                "user_id": company, 
            }
        )
        return EmbeddingCreateResponse(success=success)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error en upload_pdf: {e}")  # Añadido logging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

def extract_text_from_pdf(pdf_content: bytes) -> str:

    reader = PdfReader(io.BytesIO(pdf_content))
    text = ""
    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
    return text