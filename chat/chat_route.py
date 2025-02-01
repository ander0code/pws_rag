
from fastapi import APIRouter
from chat.chat_handlers import chat_rag_handler

chat_router = APIRouter()
chat_router.add_api_route("/chat/rag", chat_rag_handler, methods=["POST"])