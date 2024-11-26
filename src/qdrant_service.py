import numpy as np
from qdrant_client import QdrantClient
from sklearn.metrics.pairwise import cosine_similarity

# Khởi tạo Qdrant Client
client = QdrantClient(host="localhost", port=6333)
collection_name = "cv_collection"

def create_collection(vector_size=384):
    """Tạo collection trong Qdrant nếu chưa tồn tại."""
    try:
        client.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance="Cosine"
        )
        print("Collection created successfully.")
    except Exception as e:
        print("Collection already exists or error:", e)

def add_vector(vector, payload):
    """Thêm một vector vào Qdrant với metadata."""
    point_id = np.random.randint(1, 1000000)  # Tạo ID ngẫu nhiên cho vector
    client.upsert(
        collection_name=collection_name,
        points=[
            {
                "id": point_id,
                "vector": vector,
                "payload": payload
            }
        ]
    )

def search_vectors(query_vector, top_k=5):
    """Tìm kiếm các vector tương tự trong Qdrant."""
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )
    return results

def calculate_similarity(query_vector, document_vector):
    """Tính toán độ tương đồng giữa 2 vector bằng Cosine Similarity."""
    return cosine_similarity([query_vector], [document_vector])[0][0]
