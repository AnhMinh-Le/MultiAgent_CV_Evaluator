import os
import shutil
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader
from docx import Document

import streamlit as st

import streamlit as st


st.markdown("""
    <style>
        body {
            height: 100%;
            background-color: #F5F5DC; 
            background-size: cover; 
            background-position: center;
            color: #333333; 
            font-family: 'Arial', sans-serif;
        }
        .stButton > button {
            background-color: #FFD700; /* Nút màu vàng */
            color: #4B0082; /* Chữ màu tím */
            border-radius: 10px;
            padding: 10px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #4B0082; 
        }
    </style>
""", unsafe_allow_html=True)

# Nội dung ứng dụng
st.title("CV Management App ")
st.header("Choose your option:")
option = st.radio(
    "Select a feature to proceed:",
    ("Enter the folder containing the CV", "CV Compatibility Evaluation", "Chat with CV")
)


# Option 1
if option == "Enter the folder containing the CV":
    source_folder = st.text_input("Enter source folder path:", key="source_folder")
    destination_drive = st.text_input("Enter destination folder path:", key="destination_drive")

    def move_files(source_folder, destination_folder):
        # Check if destination folder exists; create if it doesn't
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for filename in os.listdir(source_folder):
            file_path = os.path.join(source_folder, filename)
            if os.path.isfile(file_path):
                shutil.move(file_path, os.path.join(destination_folder, filename))

    if source_folder and destination_drive:
        if os.path.exists(source_folder):
            move_files(source_folder, destination_drive)
            st.success(f"CVs have been classified and moved into folders: {destination_drive}")
        else:
            st.error("The source folder does not exist. Please check the path.")

# Option 2: CV Compatibility Evaluation
elif option == "CV Compatibility Evaluation":
    uploaded_folder = st.text_input("Enter the folder path containing CVs (e.g., C:/CVs):", key="uploaded_folder")
    job_description = st.text_area("Enter the job description:")

    def evaluate_compatibility(cv_text, job_description):
        # Convert text to vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([cv_text, job_description])

        # Calculate cosine similarity
        cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])
        return cosine_sim[0][0]

    def extract_text_from_pdf(pdf_path):
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            text = "".join(page.extract_text() for page in reader.pages)
        return text

    def extract_text_from_docx(docx_path):
        doc = Document(docx_path)
        return "\n".join(para.text for para in doc.paragraphs)

    if uploaded_folder and job_description:
        if os.path.exists(uploaded_folder):
            # Get list of CV files in the folder
            cv_files = [f for f in os.listdir(uploaded_folder) if f.endswith(('.txt', '.pdf', '.docx'))]

            if not cv_files:
                st.warning("No valid CV files found in the folder.")
            else:
                st.write("CVs in the folder:")
                st.write(cv_files)

                if st.button("Evaluate Compatibility"):
                    cv_scores = []
                    for cv_file in cv_files:
                        cv_file_path = os.path.join(uploaded_folder, cv_file)

                        if cv_file.endswith('.txt'):
                            with open(cv_file_path, 'r', encoding='utf-8') as f:
                                cv_text = f.read()
                        elif cv_file.endswith('.pdf'):
                            cv_text = extract_text_from_pdf(cv_file_path)
                        elif cv_file.endswith('.docx'):
                            cv_text = extract_text_from_docx(cv_file_path)

                        # Evaluate compatibility
                        similarity_score = evaluate_compatibility(cv_text, job_description)
                        cv_scores.append((cv_file, similarity_score))

                    # Sort CVs by compatibility
                    sorted_cv_scores = sorted(cv_scores, key=lambda x: x[1], reverse=True)

                    st.write("CVs sorted by compatibility with the job description:")
                    for idx, (cv_file, score) in enumerate(sorted_cv_scores):
                        st.write(f"{idx + 1}. {cv_file} - Compatibility: {score * 100:.2f}%")
        else:
            st.error("The folder path does not exist. Please check the path.")

# Option 3: Chat with CV
else:
    uploaded_folder = st.text_input("Enter the folder path containing CVs (e.g., C:/CVs):", key="chat_uploaded_folder")

    def chat_with_cv(cv_text, question):
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([cv_text, question])
        cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])
        return cosine_sim[0][0]

    if uploaded_folder:
        if os.path.exists(uploaded_folder):
            cv_files = [f for f in os.listdir(uploaded_folder) if f.endswith(('.txt', '.pdf', '.docx'))]

            if not cv_files:
                st.warning("No valid CV files found in the folder.")
            else:
                st.write("CVs in the folder:")
                st.write(cv_files)

                selected_cv = st.selectbox("Select a CV to chat with:", cv_files)
                cv_file_path = os.path.join(uploaded_folder, selected_cv)

                if selected_cv.endswith('.txt'):
                    with open(cv_file_path, 'r', encoding='utf-8') as f:
                        cv_text = f.read()
                elif selected_cv.endswith('.pdf'):
                    cv_text = extract_text_from_pdf(cv_file_path)
                elif selected_cv.endswith('.docx'):
                    cv_text = extract_text_from_docx(cv_file_path)

                question = st.text_input("Ask a question about the CV:", key="question")
                if question:
                    relevance_score = chat_with_cv(cv_text, question)
                    st.write(f"Relevance score for the question: {relevance_score:.2f}")
                    st.write("The most relevant part of the CV might be:")
                    st.write(cv_text[:500])  # Display first 500 characters as an example
        else:
            st.error("The folder path does not exist. Please check the path.")

