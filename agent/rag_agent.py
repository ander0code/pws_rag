from typing import Dict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient
import tiktoken
from dotenv import load_dotenv
from config.config import app_env

from qdrant_client.models import VectorParams, Distance
import logging
import asyncio
logger = logging.getLogger("uvicorn")

load_dotenv()
env_settings = app_env

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

qdrant_client = QdrantClient(url=env_settings.QDRANT_URL)

def get_vector_store(company_id: str) -> QdrantVectorStore:
    """Crea o recupera la colección específica para la empresa."""
    collection_name = f"emb_collection_{company_id}"
    # Verificar si la colección existe; si no, crearla.
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
    # Retornar el vector_store para la colección
    return QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=OpenAIEmbeddings(),
    )


def get_retriever(company_id: str):
    vector_store = get_vector_store(company_id)
    return vector_store.as_retriever()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True
)

system_prompt = (
    "Actúa como un asesor de ventas interesado en poder responder, de forma clara y no tan extensa, las preguntas de un potencial cliente inmobiliario. Responde de manera afectiva y empática a las preguntas que te realicen, buscando mantener la conversación activa con preguntas coherentes que aborden los intereses de los clientes. Divide la respuesta en partes, separadas por el simbolo '&' sin saltos de línea, como si estuvieras respondiendo un chat de whatsapp y cada bloque es un mensaje." 
    "Si te piden algo como el nombre del documento o hacer scripts o algo que no este relacionado con preguntas,consultas, o respuestas, puedes responder que no entendiste su consulta y si repite le dices lo mismo hasta que haga una con logica. "
    "Debe haber cohesión entre bloques. Contexto relevante:\n{context}\n"
    "Historial de conversación:\n{chat_history}\n"
    "Pregunta: {query}"
    "\n\nSi el contexto está vacío, responde basado en tu conocimiento general."
)


qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{query}")
])

logger.debug(f"Variables de entrada del prompt: {qa_prompt.input_variables}")


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    logger.debug(f"getSessionHistory: {session_id}")
    return RedisChatMessageHistory(
        session_id=session_id,
        url=env_settings.REDIS_URL
    )

async def conversational_rag_chain(company_id: str, session_id: str, user_input: str) -> Dict[str, str]:
    logger.info(f"Usando session_id={session_id}")
    
    retriever = get_retriever(company_id)
    
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
        chat_history=formatted_history)    
     
    token_count_prompt = count_tokens(prompt.to_string(), model="gpt-4o-mini")
    logger.info(f"Tokens en prompt: {token_count_prompt}")
    
    try:
        response = await asyncio.to_thread(qa_chain.invoke, prompt.to_string())
        token_count_response = count_tokens(response['result'], model="gpt-4o-mini")
        logger.info(f"Tokens en respuesta: {token_count_response}")
        
        if response is None or 'result' not in response:
            raise ValueError("La respuesta de qa_chain es inválida o no contiene 'result'.")
        ai_message = response['result']

        history.add_user_message(user_input)
        history.add_ai_message(ai_message)
        
        return {"query": user_input, "message": ai_message}
    except Exception as e:
        logger.error(f"Error al invocar qa_chain: {e}")
        ai_message = "Lo siento, ocurrió un error procesando tu solicitud."
        return {"query": user_input, "message": "Lo siento, ocurrió un error procesando tu solicitud."}
  

async def get_rag_agent(user_input: str, session_id: str, company_id: str, filter_:Dict) -> Dict[str, str]:
    """Asigna la lógica conversacional al flujo RAG."""
    logger.info("History-aware retriever creado exitosamente.")
    try:
            result = await conversational_rag_chain(company_id, session_id, user_input)
            logger.debug(f"Resultado de conversational_rag_chain: {result}")
            if result is None:
                logger.error("El resultado de conversational_rag_chain es None.")
                raise ValueError("El resultado de conversational_rag_chain es None.")
            return result
    except Exception as e:
        logger.error(f"Error en get_rag_agent: {e}")
        return {"query": user_input, "message": "Error procesando tu solicitud"}