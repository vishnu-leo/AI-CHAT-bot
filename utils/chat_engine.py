import logging
import time
import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from utils.config import GOOGLE_API_KEY
from utils.vector_store import load_vector_store
@st.cache_resource(show_spinner=False)
def get_llm():
    api_key = GOOGLE_API_KEY
    if not api_key:
        st.error("GOOGLE_API_KEY is missing from Streamlit Secrets.")
        st.stop()
    
    os.environ["GOOGLE_API_KEY"] = api_key  # Ensure it is cleanly in the environment
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.7,
        google_api_key=api_key,
        credentials=None
    )

def get_chat_response(messages: list, session_id: str = None, t_recv: float = None):
    t_start = t_recv if t_recv else time.perf_counter()
    llm = get_llm()

    # Limit to last 8 messages to reduce prompt overhead and network latency
    trimmed_messages = messages[-8:]
    formatted_messages = []
    for msg in trimmed_messages:
        if msg["role"] == "user":
            formatted_messages.append(("human", msg["content"]))
        elif msg["role"] == "assistant":
            formatted_messages.append(("ai", msg["content"]))

    latest_query = formatted_messages[-1][1] if formatted_messages else ""

    t_faiss_start = time.perf_counter()
    vectorstore = load_vector_store(session_id) if session_id else None
    t_faiss_ms = (time.perf_counter() - t_faiss_start) * 1000.0

    try:
        t_gemini_start = time.perf_counter()
        if vectorstore:
            logging.info("Using RAG workflow with retrieved context.")
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            system_prompt = (
                "You are a helpful and smart AI assistant. "
                "Use the following pieces of retrieved context to answer the user's question. "
                "If the context doesn't contain the answer, use your general knowledge, but mention that it's not from the uploaded documents. "
                "Be clear, concise, and professional.\n\n"
                "Context: {context}"
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])
            history = formatted_messages[:-1]
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            response = rag_chain.invoke({
                "input": latest_query,
                "chat_history": history
            })
            answer = response["answer"]
        else:
            logging.info("Using general conversation workflow (no RAG needed).")
            system_prompt = (
                "You are a smart, helpful, and friendly AI assistant. "
                "You can answer questions on science, technology, education, mathematics, health, history, daily life, career guidance, and general knowledge. "
                "Provide clear, concise, and helpful responses similar to a personal AI assistant. "
                "Handle greetings, casual conversations, and follow-up questions naturally."
            )
            full_prompt = [("system", system_prompt)] + formatted_messages
            response = llm.invoke(full_prompt)
            answer = response.content

        t_gemini_ms = (time.perf_counter() - t_gemini_start) * 1000.0
        t_total_ms = (time.perf_counter() - t_start) * 1000.0

        logging.info(
            f"[PERF] Session: {session_id} | "
            f"FAISS Search: {t_faiss_ms:.2f}ms | "
            f"Gemini Response: {t_gemini_ms:.2f}ms | "
            f"Total Response Time: {t_total_ms:.2f}ms"
        )
        return answer
    except Exception as e:
        logging.error(f"Gemini API generation error: {str(e)}")
        raise e

def get_chat_response_stream(messages: list, session_id: str = None):
    llm = get_llm()

    # Limit to last 8 messages to reduce prompt overhead and network latency
    trimmed_messages = messages[-8:]
    formatted_messages = []
    for msg in trimmed_messages:
        if msg["role"] == "user":
            formatted_messages.append(("human", msg["content"]))
        elif msg["role"] == "assistant":
            formatted_messages.append(("ai", msg["content"]))

    latest_query = formatted_messages[-1][1] if formatted_messages else ""

    vectorstore = load_vector_store(session_id) if session_id else None

    try:
        if vectorstore:
            logging.info("Streaming RAG workflow with retrieved context.")
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            system_prompt = (
                "You are a helpful and smart AI assistant. "
                "Use the following pieces of retrieved context to answer the user's question. "
                "If the context doesn't contain the answer, use your general knowledge, but mention that it's not from the uploaded documents. "
                "Be clear, concise, and professional.\n\n"
                "Context: {context}"
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])
            history = formatted_messages[:-1]
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            for chunk in rag_chain.pick("answer").stream({
                "input": latest_query,
                "chat_history": history
            }):
                yield chunk
        else:
            logging.info("Streaming general conversation workflow (no RAG needed).")
            system_prompt = (
                "You are a smart, helpful, and friendly AI assistant. "
                "You can answer questions on science, technology, education, mathematics, health, history, daily life, career guidance, and general knowledge. "
                "Provide clear, concise, and helpful responses similar to a personal AI assistant. "
                "Handle greetings, casual conversations, and follow-up questions naturally."
            )
            full_prompt = [("system", system_prompt)] + formatted_messages
            for chunk in llm.stream(full_prompt):
                yield chunk.content

    except Exception as e:
        logging.error(f"Gemini API generation error: {str(e)}")
        raise e
