import tiktoken
import logging
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

logger = logging.getLogger("uvicorn")

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Cuenta los tokens del texto según la codificación del modelo."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True
)

embeddings = OpenAIEmbeddings()


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