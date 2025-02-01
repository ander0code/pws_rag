from .embedding_repository import QdrantEmbeddingRepository
from typing import Dict

class IEmbeddingService:
    def save_embedding(self, content: str, metadata: Dict) -> bool:
        pass

class EmbeddingService:
    def __init__(self, repository: QdrantEmbeddingRepository):
        self.repository = repository

    def save_embedding(self, text: str, metadata: dict) -> bool:
        try:
            # Reemplazamos la llamada a upsert por el método del repositorio
            return self.repository.save_embedding(text, metadata)
        except Exception as e:
            print(f"Error al guardar embedding: {e}")
            return False

    def generate_embedding(self, text: str):
        embedding_vector = self.repository.embeddings.embed_query(text)
        return {
            "id": None,
            "vector": embedding_vector,
            "payload": {}
        }