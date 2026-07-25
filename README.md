# Smart AI Chatbot System

A full-stack AI Chatbot application built with **Python**, **FastAPI**, **Streamlit**, **LangChain**, and **FAISS**. This assistant can hold natural conversations, remember context, and perform Retrieval-Augmented Generation (RAG) on uploaded PDF documents.

## Features
- **General AI Chat**: Ask questions on science, tech, history, daily life, and more.
- **PDF Q&A**: Upload PDF documents and interactively ask questions based on their content.
- **Conversation Memory**: Remembers previous messages within the session.
- **Modern UI**: Built with Streamlit, featuring chat history, timestamps, and loading indicators.
- **Robust Backend**: Powered by FastAPI for scalable REST APIs.
- **Vector Search**: Uses FAISS for fast similarity search on documents.

## Project Structure
- `backend/`: FastAPI application, LangChain logic, and FAISS integrations.
- `frontend/`: Streamlit user interface.
- `utils/`: Configuration and shared utilities.
- `data/`: Temporary storage for uploaded files (ignored in git).
- `vectorstore/`: Persistent FAISS vector indexes (ignored in git).

## Installation & Setup

1. **Clone or Download the repository.**
2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:**
   Rename `.env.example` to `.env` and configure it:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   *Note: Do not commit `.env` to GitHub. It is safely ignored by `.gitignore`.*

## Running Locally

You need to run both the Backend (FastAPI) and Frontend (Streamlit) servers simultaneously.

**1. Start the FastAPI Backend:**
Open a terminal, activate your virtual environment, and run:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Start the Streamlit Frontend:**
Open a **new** terminal, activate your virtual environment, and run:
```bash
streamlit run frontend/app.py
```
The application will be accessible at `http://localhost:8501`.

## Cloud Deployment

This application is ready to be deployed to cloud platforms (like Render, Heroku, or AWS).

**Backend Deployment:**
- Host the FastAPI app (the root directory).
- Start command for the cloud service: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Set environment variables in the cloud dashboard:
  - `GOOGLE_API_KEY`: Your Gemini API key.
  - `BACKEND_CORS_ORIGINS`: The URL of your deployed frontend (e.g., `https://my-frontend.com`).

**Frontend Deployment (Streamlit Community Cloud or other):**
- Deploy using the root directory.
- Start command (if required): `streamlit run frontend/app.py`
- Set environment variables:
  - `FRONTEND_API_URL`: The URL of your deployed backend (e.g., `https://my-backend-api.com`).

## Security
- Your `GOOGLE_API_KEY` is completely isolated in the backend and never exposed to the frontend.
- `.gitignore` ensures that sensitive files, API keys, cache folders, and local data are never pushed to GitHub.
