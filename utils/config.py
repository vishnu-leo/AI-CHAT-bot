import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key():
    key = None
    # Try getting from Streamlit secrets first (for Streamlit Community Cloud)
    try:
        # Check if st.secrets is available without raising an exception if empty or unset
        if "GOOGLE_API_KEY" in st.secrets:
            key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    
    # Fallback to local environment variables
    if not key:
        key = os.getenv("GOOGLE_API_KEY")
        
    if key:
        return key.strip().strip("'\"")
    return None

# Configuration variables
GOOGLE_API_KEY = get_api_key()

VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

# Create required directories if they don't exist
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)
