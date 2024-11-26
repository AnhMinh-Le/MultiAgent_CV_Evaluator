from docx import Document

def load_docx(file_path):
    """Tải nội dung từ file DOCX."""
    doc = Document(file_path)
    doc_text = ""

    # Duyệt qua tất cả các đoạn văn trong DOCX
    for para in doc.paragraphs:
        doc_text += para.text
        doc_text += "\n\n"  # Tách các đoạn văn nhau

    return doc_text

def get_full_resume_text_from_docx(file_path):
    """Lấy văn bản từ file DOCX, sau đó làm sạch văn bản."""
    resume_text = load_docx(file_path)
    resume_text = clean_text(resume_text)  # Dùng hàm clean_text từ trước để xử lý văn bản

    return resume_text