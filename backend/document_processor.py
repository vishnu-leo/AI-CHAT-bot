import os
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def process_pdf(file_path: str):
    """Extracts text from a PDF file."""
    text = ""
    with open(file_path, "rb") as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def get_document_chunks(text: str):
    """Splits text into chunks for the vector store."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    # Convert to LangChain Document objects
    docs = [Document(page_content=chunk) for chunk in chunks]
    return docs
