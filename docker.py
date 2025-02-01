from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="190.237.199.97", port=6334)

collection_name = "emb_collection"
collections_response = client.get_collections()
existing_collections = [c.name for c in collections_response.collections]

if collection_name not in existing_collections:
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )