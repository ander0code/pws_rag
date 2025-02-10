from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

from typing import Dict
from dotenv import load_dotenv

from config.config import app_env
from agent.embending_agent import qdrant_client

import logging
logger = logging.getLogger("uvicorn")

load_dotenv()
env_settings = app_env
class QdrantEmbeddingRepository:
    def __init__(self):
        self.client = qdrant_client
        self.embeddings = OpenAIEmbeddings()  

    def save_embedding(self, content: str, metadata: Dict) -> bool:
        try:
            company_id = metadata.get("companyId")
            if not company_id:
                logger.error("companyId no se ha especificado en metadata.")
                return False
            
            collection_name = f"emb_collection_{metadata.get('companyId')}"
            collections_response = self.client.get_collections()
            existing_collections = [coll.name for coll in collections_response.collections]
            if collection_name not in existing_collections:
                from qdrant_client.models import VectorParams, Distance
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                logger.info(f"Colección {collection_name} creada automáticamente.")

            vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=collection_name,
                embedding=self.embeddings
            )
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
            vector_store.add_documents(docs)
            logger.info("Embeddings guardados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al guardar embedding: {e}")
            return False  