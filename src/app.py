import os
import shutil
from process import pdf_process, docx_process, translate
import classify_organize
import qdrant_service
import streamlit as st


# Streamlit UI
st.title("Resume Classification and Search App")

uploaded_files = st.file_uploader("Upload Resume Files", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    st.write("Processing files...")
    categorized_files = process_and_classify_resumes(uploaded_files)

    st.write("Categorized Resumes:")
    for category, files in categorized_files.items():
        st.write(f"**{category.capitalize()}**: {', '.join(files)}")

    description = st.text_area("Enter Job Description")
    if description:
        st.write("Searching for relevant CVs...")
        search_results = search_cv_by_description(description)

        if search_results:
            st.write(f"Found {len(search_results)} matching CV(s):")
            for result in search_results:
                st.write(f"- {result['file_name']} (Similarity: {result['similarity_score']:.2f})")
        else:
            st.write("No matching CVs found.")

else:
    st.write("Please upload some resume files to get started.")





