import os
import shutil
import streamlit as st
from process import pdf_process, docx_process, translate
import classify_organize
import qdrant_service



def classify_topic(cv_text):
    categories = [
    "Accountant", "Advocate", "Agriculture", "Apparel", "Architecture", "Arts", "Automobile", "Aviation", 
    "Banking", "Blockchain", "BPO", "Building and Construction", "Business Analyst", "Civil Engineer", 
    "Consultant", "Data Science", "Database", "Designing", "DevOps", "Digital Media", "DotNet Developer", 
    "Education", "Electrical Engineering", "ETL Developer", "Finance", "Food and Beverages", 
    "Health and Fitness", "Human Resources", "Information Technology", "Java Developer", "Management", 
    "Mechanical Engineer", "Network Security Engineer", "Operations Manager", "PMO", "Public Relations", 
    "Python Developer", "React Developer", "Sales", "SAP Developer", "SQL Developer", "Testing", "Web Designing"
]
    """Xác định topic dựa trên nội dung CV."""
    for category in categories:
        if category.lower() in cv_text.lower():
            return category
    return "Other"  # Nếu không khớp với category nào


def organize_cvs(input_folder, output_folder):
    """
    Phân loại các CV trong folder đầu vào theo category 
    và sắp xếp chúng vào các folder tương ứng trong folder đầu ra.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Duyệt qua từng file trong folder đầu vào
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # Trích xuất nội dung CV
        if filename.endswith(".pdf"):
            cv_text = extract_text_from_pdf(file_path)
        elif filename.endswith(".docx"):
            cv_text = extract_text_from_docx(file_path)
        else:
            print(f"Skipping unsupported file: {filename}")
            continue

        # Phân loại topic
        topic = classify_topic(cv_text)

        # Tạo folder theo topic nếu chưa có
        topic_folder = os.path.join(output_folder, topic)
        if not os.path.exists(topic_folder):
            os.makedirs(topic_folder)

        # Copy file vào folder tương ứng
        shutil.copy(file_path, os.path.join(topic_folder, filename))

    print(f"All CVs have been organized into: {output_folder}")


import os
import shutil
import streamlit as st
from process import pdf_process, docx_process, translate
import classify_organize
import qdrant_service


# Định nghĩa các thư mục lưu trữ tạm thời
UPLOAD_DIR = "uploaded_resumes"
OUTPUT_DIR = "organized_resumes"
OTHER_DIR = "other"

# Tạo thư mục nếu chưa tồn tại
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OTHER_DIR, exist_ok=True)


def process_and_classify_resumes(uploaded_files):
    """
    Xử lý các file CV, phân loại và tổ chức vào các thư mục theo chủ đề.
    """
    categorized_files = {category: [] for category in classify_organize.CATEGORIES}
    categorized_files["other"] = []

    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_DIR, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        # Xử lý các loại file PDF và DOCX
        if file.name.endswith(".pdf"):
            resume_text = pdf_process.get_full_resume_text(file_path)
        elif file.name.endswith(".docx"):
            resume_text = docx_process.get_full_resume_text_from_docx(file_path)
        else:
            continue

        # Phân loại chủ đề của CV
        topic = classify_organize.classify_topic(resume_text)
        
        # Di chuyển CV vào thư mục phù hợp
        if topic in classify_organize.CATEGORIES:
            target_dir = os.path.join(OUTPUT_DIR, topic)
        else:
            topic = "other"
            target_dir = os.path.join(OUTPUT_DIR, OTHER_DIR)

        os.makedirs(target_dir, exist_ok=True)
        shutil.move(file_path, os.path.join(target_dir, file.name))

        # Lưu trữ vào Qdrant
        qdrant_service.add_vector_to_qdrant(resume_text, topic, file.name)

        # Lưu tên file vào danh sách đã phân loại
        categorized_files[topic].append(file.name)

    return categorized_files

