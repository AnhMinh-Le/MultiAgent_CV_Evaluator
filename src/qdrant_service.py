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
QDRANT_URL = ""  # Điền URL của Qdrant Cloud
QDRANT_API_KEY = ""  # Điền API key của Qdrant Cloud
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def extract_extension(file_name):
    """
    Trích xuất phần mở rộng (extension) của file.
    Ví dụ: 'file.pdf' -> 'pdf'
    """
    return os.path.splitext(file_name)[1][1:].lower()

def extract_id_from_filename(file_name):
    """
    Trích xuất ID từ tên file, tạo UUID từ tên file.
    """
    base_name = os.path.splitext(file_name)[0]  # Loại bỏ phần mở rộng .pdf
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base_name))  # Tạo UUID từ tên file

### HÀM QUẢN LÝ COLLECTION TRÊN QDRANT ###
def create_or_replace_collection():
    """
    Kiểm tra và thay thế collection trên Qdrant nếu đã tồn tại.
    """
    try:
        collections = [col.name for col in qdrant_client.get_collections().collections]
        if COLLECTION_NAME in collections:
            print(f"Collection '{COLLECTION_NAME}' already exists. Deleting it...")
            qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' deleted.")
        
        # Tạo collection mới
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION_NAME}' created.")
    except Exception as e:
        print(f"Error managing collection: {e}")


### HÀM XỬ LÝ FILE ###
def process_file(file_path, file_name):
    """
    Xử lý từng file CV (PDF hoặc DOCX), tạo nhúng, và lưu vào Qdrant.
    """
    try:
        # Đọc nội dung file
        if file_name.endswith(".pdf"):
            content = get_full_resume_text(file_path)
        elif file_name.endswith(".docx"):
            content = get_full_resume_text_from_docx(file_path)
        else:
            print(f"Unsupported file format: {file_name}")
            return

        # Sinh vector nhúng
        cv_vector = model.encode(content).tolist()
        if not cv_vector:
            print(f"No embedding generated for {file_name}")
            return

        # Lưu vector và metadata vào Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[{
                "id": extract_id_from_filename(file_name),  # Sử dụng tên file làm ID
                "vector": cv_vector,
                "payload": {
                    "source_type": extract_extension(file_name),
                    "id": extract_id_from_filename(file_name),
                    "file_name": file_name,
                    "text_content": content,
                },
            }]
        )
        print(f"Processed and stored: {file_name}")
    except Exception as e:
        print(f"Error processing file {file_name}: {e}")


### HÀM XỬ LÝ TOÀN BỘ THƯ MỤC ###
def process_folder_to_qdrant(folder_path):
    """
    Duyệt qua thư mục chứa CV, xử lý từng file, và lưu kết quả vào Qdrant.
    """
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            continue
        process_file(file_path, file_name)

    print("All CVs processed and added to Qdrant.")


### CHƯƠNG TRÌNH CHÍNH ###
if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing CVs: ").strip()

    # Kiểm tra hoặc thay thế collection
    create_or_replace_collection()

    # Xử lý folder
    process_folder_to_qdrant(folder_path)

    print("Processing completed.")