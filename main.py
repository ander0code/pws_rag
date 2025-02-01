from fastapi import FastAPI
from session.session_route import session_router
from chat.chat_route import chat_router
from embedding.embedding_router import embedding_route
from session.session_middleware import SessionMiddleware
from config.config import app_env
from dotenv import load_dotenv
import logging

load_dotenv()
env_settings = app_env

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="RAG PWS",
    version="1.0.0",
    description="Migrado de TypeScript a Python (FastAPI)",
)


app.add_middleware(SessionMiddleware)
app.include_router(session_router)
app.include_router(chat_router)
app.include_router(embedding_route)

if __name__ == "__main__":
    import uvicorn
    port = env_settings.APP_PORT or 3000
    print(f"Server is running on http://localhost:{port}")
    uvicorn.run(app, host="localhost", port=port)