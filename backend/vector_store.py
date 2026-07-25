import os
import logging
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.config import VECTOR_STORE_PATH, GOOGLE_API_KEY

_CACHED_EMBEDDING_MODEL = None
_GLOBAL_EMBEDDINGS = None
_FAISS_CACHE = {}

def get_supported_embedding_model() -> str:
    global _CACHED_EMBEDDING_MODEL
    if _CACHED_EMBEDDING_MODEL:
        return _CACHED_EMBEDDING_MODEL

    try:
        from google import genai
        import os
        api_key_str = os.getenv("GOOGLE_API_KEY", "").strip().strip("'\"")
        client = genai.Client(api_key=api_key_str)
        for model in client.models.list():
            if model.supported_actions and "embedContent" in model.supported_actions:
                logging.info(f"Dynamically discovered supported embedding model: {model.name}")
                _CACHED_EMBEDDING_MODEL = model.name
                return _CACHED_EMBEDDING_MODEL
    except Exception as e:
        logging.warning(f"Could not dynamically list models ({str(e)}), falling back to default supported model.")

    _CACHED_EMBEDDING_MODEL = "models/gemini-embedding-001"
    return _CACHED_EMBEDDING_MODEL

def get_embeddings():
    global _GLOBAL_EMBEDDINGS
    if _GLOBAL_EMBEDDINGS is not None:
        return _GLOBAL_EMBEDDINGS

    import os
    api_key_str = os.getenv("GOOGLE_API_KEY")
    if not api_key_str:
        raise ValueError("Google API Key not found. Please set GOOGLE_API_KEY in your .env file or environment.")
    api_key = api_key_str.strip().strip("'\"")
    os.environ["GOOGLE_API_KEY"] = api_key  # Cleanly set it in environ
    
    model_name = get_supported_embedding_model()
    _GLOBAL_EMBEDDINGS = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=api_key)
    return _GLOBAL_EMBEDDINGS

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
