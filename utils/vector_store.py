import os
import logging
import streamlit as st
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.config import VECTOR_STORE_PATH, GOOGLE_API_KEY

_FAISS_CACHE = {}

@st.cache_resource(show_spinner=False)
def get_embeddings():
    api_key = GOOGLE_API_KEY
    if not api_key:
        st.error("Google API Key not found. Please set GOOGLE_API_KEY in your Streamlit secrets or .env file.")
        st.stop()
    
    os.environ["GOOGLE_API_KEY"] = api_key  # Cleanly set it in environ
    
    # Use the currently supported and standard embedding model for Gemini
    model_name = "models/text-embedding-004"
    return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=api_key)

def save_vector_store(docs, session_id: str):
    """Creates a vector store from documents and saves it locally and in-memory cache."""
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    path = os.path.join(VECTOR_STORE_PATH, session_id)
    vectorstore.save_local(path)
    _FAISS_CACHE[session_id] = vectorstore
    return True

def load_vector_store(session_id: str):
    """Loads a vector store from in-memory cache or disk."""
    if not session_id:
        return None
        
    if session_id in _FAISS_CACHE:
        return _FAISS_CACHE[session_id]

    path = os.path.join(VECTOR_STORE_PATH, session_id)
    if not os.path.exists(path):
        return None
    
    embeddings = get_embeddings()
    # allow_dangerous_deserialization=True is required for loading FAISS index in newer LangChain versions
    vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    _FAISS_CACHE[session_id] = vectorstore
    return vectorstore
