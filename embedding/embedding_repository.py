from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

from typing import Dict
from dotenv import load_dotenv

from config.config import app_env
from agent.rag_agent import qdrant_client

import logging
logger = logging.getLogger("uvicorn")

load_dotenv()
env_settings = app_env
class QdrantEmbeddingRepository:
    def __init__(self):
        self.client = qdrant_client
        self.collection_name = "emb_collection"
        self.embeddings = OpenAIEmbeddings()  
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings  
        )

    def save_embedding(self, content: str, metadata: Dict) -> bool:
        try:
            text_splitter = CharacterTextSplitter()
            chunks = text_splitter.split_text(content)
            docs = [
                Document(
                    page_content=chunk,
                    metadata={
                        "companyId": metadata.get("companyId"),
                        "userId": metadata.get("userId"),
                        "source": metadata.get("source")
                    }
                )
                for chunk in chunks
            ]
            self.vector_store.add_documents(docs)
            logger.info("Embeddings guardados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al guardar embedding: {e}")
            return False  # Corregido de 'F' a 'False'