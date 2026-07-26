# Smart AI Chatbot System

A unified AI Chatbot application built with **Python**, **Streamlit**, **LangChain**, and **FAISS**. This assistant can hold natural conversations, remember context, and perform Retrieval-Augmented Generation (RAG) on uploaded PDF documents.

## Features
- **General AI Chat**: Ask questions on science, tech, history, daily life, and more.
- **PDF Q&A**: Upload PDF documents and interactively ask questions based on their content.
- **Conversation Memory**: Remembers previous messages within the session.
- **Modern UI**: Built with Streamlit, featuring chat history, timestamps, and loading indicators.
- **Unified Architecture**: Everything runs directly within Streamlit for easy deployment on Streamlit Community Cloud.
- **Vector Search**: Uses FAISS for fast similarity search on documents.

## Project Structure
- `frontend/`: Streamlit user interface (`app.py`).
- `utils/`: Configuration and shared modules (document processing, chat engine, vector store).
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

To run the application locally:
```bash
streamlit run frontend/app.py
```
The application will be accessible at `http://localhost:8501`.

## Cloud Deployment (Streamlit Community Cloud)

This application is ready to be deployed to Streamlit Community Cloud.

1. Push your repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and create a new app.
3. Select your repository, branch, and set the **Main file path** to `frontend/app.py`.
4. Click on **Advanced settings** (or the **Secrets** section).
5. Add your Google API Key to the Streamlit secrets:
   ```toml
   GOOGLE_API_KEY = "your_actual_api_key_here"
   ```
6. Click **Deploy!**

## Security
- Make sure not to expose your `GOOGLE_API_KEY` in source code. Use Streamlit Secrets for cloud deployment and `.env` for local execution.
- `.gitignore` ensures that sensitive files, API keys, cache folders, and local data are never pushed to GitHub.
