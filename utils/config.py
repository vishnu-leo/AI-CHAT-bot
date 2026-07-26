import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Forcefully disable Google Cloud OAuth Application Default Credentials (ADC)
# This ensures that ONLY the API key is used, preventing ACCESS_TOKEN_TYPE_UNSUPPORTED errors.
for key in ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_APPLICATION_CREDENTIALS_JSON", "GOOGLE_CLOUD_PROJECT", "GCP_PROJECT", "GCLOUD_PROJECT"]:
    os.environ.pop(key, None)

def get_api_key():
    # Read strictly from environment (loaded via .env locally or injected by Streamlit Cloud)
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
