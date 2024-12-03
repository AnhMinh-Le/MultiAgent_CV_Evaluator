import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from docx import Document
import torch
from process.pdf_process import get_full_resume_text
from process.docx_process import get_full_resume_text_from_docx
import requests
import time
import uuid

os.environ["TRANSFORMERS_CACHE"] = r"E:\Github Repo\transformers_cache"

# Khởi tạo mô hình nhúng cục bộ
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
VECTOR_SIZE = 768  # Kích thước vector
model = SentenceTransformer(MODEL_NAME)

# Thông tin Qdrant
COLLECTION_NAME = "CV_Database"
QDRANT_URL = "https://32b1319b-5136-4662-8a88-f0004f1e3070.europe-west3-0.gcp.cloud.qdrant.io:6333"  # Điền URL của Qdrant Cloud
QDRANT_API_KEY = "bOfzMx3URIVaGm2YmYm1fchZoLF5WUi0Q9Kod2mPg9EIj1OZ4Bid6Q"  # Điền API key của Qdrant Cloud
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def retrieve_by_id(file_id):
    """
    Lấy thông tin metadata của một CV từ Qdrant dựa trên ID.
    """
    try:
        # Truy vấn điểm từ Qdrant bằng ID
        result = qdrant_client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[file_id]  # ID của điểm cần truy vấn
        )
        
        if result:
            for point in result:
                print(f"ID: {point.id}")
                print(f"Payload: {point.payload}")  # In metadata của điểm
        else:
            print(f"No result found for ID: {file_id}")
    except Exception as e:
        print(f"Error retrieving point: {e}")

# Ví dụ sử dụng
if __name__ == "__main__":
    file_id = input("Enter the ID of the file to retrieve: ")
    retrieve_by_id(file_id)