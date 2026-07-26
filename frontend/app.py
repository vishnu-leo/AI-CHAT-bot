import streamlit as st
import json
import os
import shutil
import sys
from datetime import datetime

# Add the project root to sys.path to allow importing from utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests

API_URL = "http://localhost:8000"

# Configure Streamlit page
st.set_page_config(
    page_title="AI Chatbot Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import base64

# Minimal AI Robot SVG
ai_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a5 5 0 0 1 5 5v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7a5 5 0 0 1 5-5h1V5.73A2 2 0 0 1 12 2z"/><circle cx="9" cy="13" r="1" fill="#3b82f6" stroke="none"/><circle cx="15" cy="13" r="1" fill="#3b82f6" stroke="none"/><path d="M10 17h4"/></svg>"""
AI_AVATAR = f"data:image/svg+xml;base64,{base64.b64encode(ai_svg.encode('utf-8')).decode('utf-8')}"

USER_AVATAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>"""

def render_message(role, content, timestamp=None):
    if role == "user":
        html = f"""
<div class="user-message-row">
    <div class="user-message-bubble">

{content}

{f'<div class="chat-timestamp right">{timestamp}</div>' if timestamp else ''}
    </div>
    <div class="user-avatar">{USER_AVATAR_SVG}</div>
</div>
"""
    else:
        html = f"""
<div class="ai-message-row">
    <div class="ai-avatar"><img src="{AI_AVATAR}"></div>
    <div class="ai-message-bubble">

{content}

{f'<div class="chat-timestamp left">{timestamp}</div>' if timestamp else ''}
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

# Custom CSS for UI Redesign
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* Global Font */
html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'Inter', sans-serif !important;
}

/* Background & Main Container */
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important;
}
[data-testid="stSidebar"] hr {
    border-color: #f1f5f9;
}

/* Hide Streamlit Footer */
footer { display: none !important; }

/* Main layout padding */
.block-container {
    padding-top: 60px !important;
    padding-bottom: 120px !important;
    max-width: 900px !important;
}

/* Floating Badge */
.header-container {
    text-align: center;
    width: 100%;
    padding-top: 10px;
    margin-bottom: 40px;
}
.floating-badge {
    display: inline-block;
    background: linear-gradient(90deg, #ff7e5f, #feb47b);
    color: white;
    padding: 8px 24px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(255, 126, 95, 0.4);
    letter-spacing: 0.5px;
}

/* Document & Sidebar Elements */
h1, h2, h3 {
    color: #0f172a !important;
}

/* PDF Upload Card */
[data-testid="stFileUploader"] {
    background: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6;
    background: #eff6ff;
}

/* Custom Message Layouts */
.user-message-row {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    width: 100%;
    margin-bottom: 24px;
}
.user-message-bubble {
    background-color: #f8fafc;
    color: #1e293b;
    padding: 14px 20px;
    border-radius: 20px;
    border-top-right-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    margin-right: 12px;
    max-width: 80%;
    text-align: left;
}
.user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #ffffff;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
    flex-shrink: 0;
}
.user-avatar svg {
    width: 22px;
    height: 22px;
    fill: #94a3b8;
}

.ai-message-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    width: 100%;
    margin-bottom: 24px;
}
.ai-message-bubble {
    background-color: #ffffff;
    color: #0f172a;
    padding: 14px 20px;
    border-radius: 20px;
    border-top-left-radius: 4px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    margin-left: 12px;
    max-width: 80%;
    text-align: left;
}
.ai-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #ffffff;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
    flex-shrink: 0;
}
.ai-avatar img {
    width: 22px;
    height: 22px;
}

/* Timestamps */
.chat-timestamp {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 6px;
}
.chat-timestamp.right { text-align: right; }
.chat-timestamp.left { text-align: left; }

/* Responsive */
@media (max-width: 768px) {
    .user-message-bubble, .ai-message-bubble {
        max-width: 85%;
    }
}

/* Loading Indicator animation */
@keyframes pulse {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}
.loading-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    color: #64748b;
    font-size: 14px;
    font-style: italic;
    background: #ffffff;
    border-radius: 20px;
    border-bottom-left-radius: 4px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    width: fit-content;
    margin-bottom: 24px;
    margin-left: 48px;
}
.loading-indicator span {
    width: 6px;
    height: 6px;
    background-color: #3b82f6;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out both;
}
.loading-indicator span:nth-child(1) { animation-delay: -0.32s; }
.loading-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* Chat Input Styling */
[data-testid="stBottomBlockContainer"] {
    background: transparent !important;
    padding-bottom: 20px !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* The actual input pill */
[data-testid="stChatInput"] > div {
    background-color: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    border-radius: 40px !important;
    padding: 4px 6px 4px 20px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.06) !important;
    margin: 0 auto !important;
    max-width: 800px !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #1e293b !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding-top: 14px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
}

/* Send Button */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    margin-top: 2px !important;
    margin-right: 2px !important;
    transition: all 0.2s !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stChatInput"] button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}
[data-testid="stChatInput"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
    width: 18px !important;
    height: 18px !important;
}

/* Hide default title padding */
.stTitle { display: none !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# API URLs removed since we are running everything in Streamlit

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "default_session"
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

# Sidebar Panel
with st.sidebar:
    st.markdown("<h2 style='margin-bottom: 0;'>Document Q&A</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Upload a PDF to chat with its contents.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # File info display
        file_size = round(uploaded_file.size / (1024 * 1024), 2)
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 12px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e2e8f0;">
            <div style="font-weight: 500; color: #1e293b; font-size: 14px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{uploaded_file.name}</div>
            <div style="color: #64748b; font-size: 12px; margin-top: 4px;">{file_size} MB</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Process Document", use_container_width=True):
            with st.spinner("Processing document..."):
                try:
                    session_id = st.session_state.session_id
                    
                    # Send to FastAPI backend
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"session_id": session_id}
                    
                    response = requests.post(f"{API_URL}/upload", files=files, data=data)
                    
                    if response.status_code == 200:
                        st.session_state.pdf_uploaded = True
                        st.success("Document processed successfully! You can now ask questions about it.")
                    else:
                        st.error(f"Error processing document: {response.text}")
                except Exception as e:
                    st.error(f"Error uploading document: {str(e)}")
                    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 5px; font-size: 16px;'>About</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 13px;'>Powered by <b>LangChain</b>, <b>Streamlit</b>, <b>FAISS</b>, and <b>Google Gemini</b>.</p>", unsafe_allow_html=True)

# Main Chat Header
st.markdown("""
<div class="header-container">
    <div class="floating-badge">AI Chatbot</div>
</div>
""", unsafe_allow_html=True)

# Empty State Greeting
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align: center; margin-top: 10vh;'>
        <h1 style='color: #1e293b; font-size: 32px; font-weight: 600; letter-spacing: -0.5px;'>How can I help you today?</h1>
        <p style='color: #64748b; font-size: 16px; margin-top: 10px;'>Ask any question or upload a document to get started.</p>
    </div>
    """, unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    render_message(message["role"], message["content"], message.get("timestamp"))

# Chat Input
if prompt := st.chat_input("Type something..."):
    current_time = datetime.now().strftime("%I:%M %p")
    
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": current_time})
    
    # 2. Display user message
    render_message("user", prompt, current_time)
        
    # 3. Generate & display AI response
    placeholder = st.empty()
    placeholder.markdown('<div class="loading-indicator"><span></span><span></span><span></span> AI is thinking...</div>', unsafe_allow_html=True)
    
    try:
        # Prepare payload
        payload = {
            "messages": st.session_state.messages[-10:],
            "session_id": st.session_state.session_id if st.session_state.pdf_uploaded else None
        }
        
        # Call FastAPI stream endpoint
        response = requests.post(f"{API_URL}/chat", json=payload, stream=True)
        response.raise_for_status()
        
        placeholder.empty()
        
        ai_placeholder = st.empty()
        assistant_response = ""
        
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                assistant_response += chunk
                
                # Update placeholder dynamically
                html = f"""
<div class="ai-message-row">
    <div class="ai-avatar"><img src="{AI_AVATAR}"></div>
    <div class="ai-message-bubble">

{assistant_response}

    </div>
</div>
"""
                ai_placeholder.markdown(html, unsafe_allow_html=True)
        
        resp_time = datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({"role": "assistant", "content": assistant_response, "timestamp": resp_time})
        
        # Final render with timestamp
        final_html = f"""
<div class="ai-message-row">
    <div class="ai-avatar"><img src="{AI_AVATAR}"></div>
    <div class="ai-message-bubble">

{assistant_response}

<div class="chat-timestamp left">{resp_time}</div>
    </div>
</div>
"""
        ai_placeholder.markdown(final_html, unsafe_allow_html=True)

    except Exception as e:
        placeholder.empty()
        st.error(f"Error generating response: {str(e)}")
