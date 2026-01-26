from qdrant_client import QdrantClient, models

client = QdrantClient(url="localhost", port=6333)
collection = client.get_collection("credit_apps")
