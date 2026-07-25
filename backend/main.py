import os
import shutil
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional

from utils.config import DATA_PATH, GOOGLE_API_KEY
from backend.document_processor import process_pdf, get_document_chunks
from backend.vector_store import save_vector_store
from backend.chat_engine import get_chat_response, get_llm, get_chat_response_stream_async

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up backend...")
    if not GOOGLE_API_KEY:
        logging.error("GOOGLE_API_KEY is missing in the environment variables!")
    else:
        logging.info("GOOGLE_API_KEY is present.")
        try:
            # Test Gemini connection
            llm = get_llm()
            logging.info("Sending startup test request to Gemini API...")
            response = llm.invoke("Hello, this is a startup test.")
            logging.info(f"Successfully connected to Gemini API. Test response: {response.content}")
        except ValueError as ve:
            logging.error(f"Configuration Error: {str(ve)}")
        except Exception as e:
            error_str = str(e)
            if "API_KEY_INVALID" in error_str or "API key not valid" in error_str:
                logging.error(
                    "Startup Test Failed: The provided GOOGLE_API_KEY is invalid or rejected by Google. "
                    "Exact reason: API key not valid. Please ensure you copied the key correctly from Google AI Studio."
                )
            else:
                logging.error(f"Failed to connect to Gemini API on startup: {error_str}")
    
    yield
    logging.info("Shutting down backend...")

app = FastAPI(title="AI Chatbot API", lifespan=lifespan)

cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    session_id: Optional[str] = "default"

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Chatbot API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        logging.info(f"Received chat request for session: {request.session_id}")
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
            
        response_text = get_chat_response(request.messages, request.session_id)
        logging.info("Successfully generated response from Gemini.")
        return {"response": response_text}
    except Exception as e:
        logging.error(f"Error in /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat_stream")
async def chat_stream(request: ChatRequest):
    try:
        logging.info(f"Received stream request for session: {request.session_id}")
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
            
        return StreamingResponse(get_chat_response_stream_async(request.messages, request.session_id), media_type="text/plain")
    except Exception as e:
        logging.error(f"Error in /chat_stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form("default")
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        file_path = os.path.join(DATA_PATH, f"{session_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        text = process_pdf(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF")
            
        chunks = get_document_chunks(text)
        save_vector_store(chunks, session_id)
        os.remove(file_path)
        
        logging.info(f"Successfully processed PDF: {file.filename}")
        return {"status": "success", "message": f"Successfully processed {file.filename} and updated knowledge base."}
    except Exception as e:
        logging.error(f"Error in /upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
