import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

# Create required directories if they don't exist
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)
