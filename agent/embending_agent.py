import asyncio
import logging
from agent.agent import llm, count_tokens, qa_prompt, embeddings
from config.config import app_env
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain.chains import RetrievalQA
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory

logger = logging.getLogger("uvicorn")

qdrant_client = QdrantClient(url=app_env.QDRANT_URL)

def get_vector_store(company_id: str) -> QdrantVectorStore:
    """
    Obtiene (o crea) la colección en Qdrant y retorna un vector store.
    """
    collection_name = f"emb_collection_{company_id}"

    try:
        qdrant_client.get_collection(collection_name=collection_name)
        logger.info(f"Colección {collection_name} encontrada.")
    except Exception as e:
        logger.info(f"Colección {collection_name} no encontrada. Creándola. Detalle: {e}")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
        logger.info(f"Colección {collection_name} creada automáticamente.")
    
    return QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embeddings,
    )

def get_session_history(session_id: str):
    """
    Retorna el historial de conversación usando Redis.
    """
    logger.debug(f"Obteniendo historial para session_id: {session_id}")
    return RedisChatMessageHistory(
        session_id=session_id,
        url=app_env.REDIS_URL
    )

async def conversational_rag_chain(company_id: str, session_id: str, user_input: str) -> dict:
    """
    Ejecuta la cadena de RAG usando un vector store para recuperar contexto y el LLM para generar la respuesta.
    """
    vector_store = get_vector_store(company_id)
    retriever = vector_store.as_retriever()
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        input_key="query",
        return_source_documents=True
    )
    
    history = get_session_history(session_id)
    past_messages = await history.aget_messages()
    formatted_history = [
        {"role": "user" if msg.type == 'human' else "assistant", "content": msg.content}
        for msg in past_messages
    ]
    
    prompt = qa_prompt.format_prompt(
        context="",
        query=user_input,
        chat_history=formatted_history
    )
    token_count_prompt = count_tokens(prompt.to_string(), model="gpt-4o-mini")
    logger.info(f"Tokens en prompt: {token_count_prompt}")
    
    try:
        response = await asyncio.to_thread(qa_chain.invoke, prompt.to_string())
        token_count_response = count_tokens(response.get('result', ''), model="gpt-4o-mini")
        logger.info(f"Tokens en respuesta: {token_count_response}")
        if not response or 'result' not in response:
            raise ValueError("Respuesta inválida de qa_chain.")
        ai_message = response['result']
        history.add_user_message(user_input)
        history.add_ai_message(ai_message)
        return {"query": user_input, "message": ai_message}
    except Exception as e:
        logger.error(f"Error al invocar qa_chain: {e}")
        return {"query": user_input, "message": "Lo siento, ocurrió un error procesando tu solicitud."}