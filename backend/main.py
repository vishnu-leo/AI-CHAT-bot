import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from utils.chat_engine import get_chat_response_stream
from utils.document_processor import process_pdf, get_document_chunks
from utils.vector_store import save_vector_store
from utils.config import DATA_PATH

app = FastAPI(title="AI Chatbot Backend")

# Allow Streamlit frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        def stream_generator():
            try:
                for chunk in get_chat_response_stream(messages_dict, request.session_id):
                    if chunk:
                        yield chunk
            except Exception as e:
                yield f"Error: {str(e)}"
                
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_endpoint(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        file_path = os.path.join(DATA_PATH, f"{session_id}_{file.filename}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        text = process_pdf(file_path)
        if not text.strip():
            raise ValueError("Could not extract text from the PDF")
            
        chunks = get_document_chunks(text)
        save_vector_store(chunks, session_id)
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return {"success": True, "message": "Document processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
