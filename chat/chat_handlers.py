from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from agent.embending_agent import get_vector_store
from agent.response_agent import get_response_agent
from concurrent.futures import ThreadPoolExecutor
import orjson
import logging


logger = logging.getLogger("uvicorn")

executor = ThreadPoolExecutor(max_workers=1)
 
def sync_stream(generator):
    try:
        for item in generator:
            yield item
    except Exception as e:
        logger.error(f"Error en el generador: {e}")
        raise e 

async def chat_rag_handler(request: Request) -> StreamingResponse:
    try:
        data = await request.json()
        chat_session_id = request.headers.get("chat_session")
        company_id = request.headers.get("company")

        if not chat_session_id:
            raise HTTPException(status_code=400, detail="Falta el header 'chat_session'")
        if not company_id:
            raise HTTPException(status_code=400, detail="Falta el header 'company'")
        
        logger.debug(f"chat_session ID: {chat_session_id}")
        logger.debug(f"Company ID: {company_id}")

        user_input = data.get("message")
        logger.debug(f"mensaje: {user_input}")
        if not user_input:
            raise HTTPException(status_code=400, detail="Falta el mensaje en el cuerpo de la solicitud")

        filter_ = {
            "must": [
                {"key": "companyId",  "match": {"value": int(company_id)}},
                {"key": "ChatSessionId", "match": {"value": chat_session_id}},
            ],
            "retriever": get_vector_store(company_id)
        }

        conversational_rag_chain = await get_response_agent(user_input, chat_session_id,company_id,filter_)
        logger.debug(f"Resultado de handle_user_question: {conversational_rag_chain}")
        
        if not conversational_rag_chain or "message" not in conversational_rag_chain:
            async def error_stream():
                error_msg = {"result": "No se pudo generar una respuesta"}
                yield orjson.dumps(error_msg) + b"\n"
                
            return StreamingResponse(error_stream(), media_type="application/json")

        async def content_stream():
            message = conversational_rag_chain.get("message", "...")
            line = {"result": message}
            yield orjson.dumps(line) + b"\n"

        return StreamingResponse(content_stream(), media_type="application/json")

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error en chat_rag_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))