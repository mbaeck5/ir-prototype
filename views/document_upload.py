import streamlit as st
from datetime import datetime
from utils.document_processing import extract_text_from_pdf, extract_text_from_docx
def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    selected_quarter = {} if 'selected_quarter' not in st.session_state else st.session_state['selected_quarter']
    fiscal_year = {} if 'fiscal_year' not in st.session_state else st.session_state['fiscal_year']

    st.header(f"Document Upload and Analysis - {company_name} {selected_quarter} FY{fiscal_year}")

    uploaded_files = st.file_uploader(
        "Upload earnings calls, competitor analysis, or other relevant documents",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt']
    )

    if uploaded_files:
        for file in uploaded_files:
            file_key = f"{file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if file_key not in st.session_state.uploaded_files:
                file_bytes = file.read()
                file_type = file.name.split('.')[-1].lower()

                if file_type == 'pdf':
                    text_content = extract_text_from_pdf(file_bytes)
                elif file_type == 'docx':
                    text_content = extract_text_from_docx(file_bytes)
                elif file_type == 'txt':
                    text_content = file_bytes.decode('utf-8')
                else:
                    text_content = "Unsupported file type"

                st.session_state.uploaded_files[file_key] = {
                    'name': file.name,
                    'content': text_content,
                    'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                st.success(f"Successfully uploaded: {file.name}")

    # Display uploaded documents
    if st.session_state.uploaded_files:
        st.subheader("Uploaded Documents")
        for file_key, file_data in st.session_state.uploaded_files.items():
            st.write(f"📄 {file_data['name']} - Uploaded at {file_data['upload_time']}")
            if st.button(f"View Content", key=f"view_{file_key}"):
                st.text_area("Document Content", file_data['content'], height=300)