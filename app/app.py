# app.py
import streamlit as st
import google.generativeai as genai
import json
import os

# ----------------------------
# CONFIGURE GOOGLE GEMINI API
# ----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # Replace with your real API key
MODEL_NAME = "gemini-2.5-flash"

# ----------------------------
# FILE PATHS
# ----------------------------
DATA_PATHS = [
    r"data/statutes.json",
    r"data/judgments.json"
]
CHAT_HISTORY_FILE = "chat_history.json"

# ----------------------------
# LOAD LEGAL DATA
# ----------------------------
legal_docs = []
for path in DATA_PATHS:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            legal_docs.extend(json.load(f))

# ----------------------------
# STREAMLIT CONFIG
# ----------------------------
st.set_page_config(page_title="Criminal Law Chatbot", page_icon="⚖")
st.title("⚖ Criminal Law Chatbot")
st.caption("Ask questions about Indian Criminal Law, IPC sections, or legal case references.")

# ----------------------------
# SESSION STATE INITIALIZATION
# ----------------------------
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {}
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = "General Chat"

# Load persisted chat history
if os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
        st.session_state["chat_sessions"] = json.load(f)

# Initialize messages for current chat
if st.session_state["current_chat"] not in st.session_state["chat_sessions"]:
    st.session_state["chat_sessions"][st.session_state["current_chat"]] = {"messages": []}

messages = st.session_state["chat_sessions"][st.session_state["current_chat"]]["messages"]

# ----------------------------
# CHAT THREAD SELECTION
# ----------------------------
st.sidebar.title("Chats")
if st.sidebar.button("New Chat"):
    chat_name = f"Chat {len(st.session_state['chat_sessions']) + 1}"
    st.session_state["chat_sessions"][chat_name] = {"messages": []}
    st.session_state["current_chat"] = chat_name
    messages = st.session_state["chat_sessions"][st.session_state["current_chat"]]["messages"]

chat_selection = st.sidebar.selectbox(
    "Select Chat",
    list(st.session_state["chat_sessions"].keys()),
    index=list(st.session_state["chat_sessions"].keys()).index(st.session_state["current_chat"])
)
st.session_state["current_chat"] = chat_selection
messages = st.session_state["chat_sessions"][st.session_state["current_chat"]]["messages"]

# ----------------------------
# USER INPUT
# ----------------------------
if "input_box_text" not in st.session_state:
    st.session_state["input_box_text"] = ""

user_input = st.text_input(
    "Enter your question:",
    value=st.session_state["input_box_text"],
    key="input_box_text",
    placeholder="Type your question and press Enter"
)

# ----------------------------
# SEND MESSAGE AUTOMATICALLY
# ----------------------------
if user_input.strip():
    # Add user message
    messages.append({"role": "user", "text": user_input})

    # Build context from local statutes/judgments
    context_snippets = []
    for d in legal_docs:
        text = d.get("text", "")
        if user_input.lower() in text.lower():
            context_snippets.append(text)
    context = "\n".join(context_snippets[:5])

    # Build conversation history for AI context
    full_chat_context = "\n".join([f"{m['role']}: {m['text']}" for m in messages])

    # Prepare prompt
    prompt = f"""
You are an expert Indian criminal law assistant.
Use the previous conversation and the following statutes/judgments context to answer
precisely.
Conversation history:
{full_chat_context}
Context from local data:
{context or "No relevant context found"}
Question:
{user_input}
Answer concisely in simple legal terms, citing IPC sections or examples where possible.
"""

    # Generate bot response
    with st.spinner("Generating response..."):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            bot_text = response.text
        except Exception as e:
            bot_text = f"❌ Error generating response: {str(e)}"

    # Add bot message
    messages.append({"role": "bot", "text": bot_text})

    # Clear the input box
    st.session_state["input_box_text"] = ""

    # Persist chat history
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state["chat_sessions"], f, indent=2, ensure_ascii=False)

# ----------------------------
# DISPLAY CHAT BUBBLES (DARK MODE)
# ----------------------------
st.markdown("<hr>", unsafe_allow_html=True)
for msg in messages[-50:]:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style="
                text-align:right;
                background-color:#1E4620;
                color:#FFFFFF;
                border-radius:15px;
                padding:10px;
                margin:5px;
                display:inline-block;
                max-width:80%;
                font-size:14px;
                float:right;
                clear:both;
            ">{msg['text']}</div>
            <div style="clear:both;"></div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                text-align:left;
                background-color:#2C2C2C;
                color:#FFFFFF;
                border-radius:15px;
                padding:10px;
                margin:5px;
                display:inline-block;
                max-width:80%;
                font-size:14px;
                float:left;
                clear:both;
            ">{msg['text']}</div>
            <div style="clear:both;"></div>
            """,
            unsafe_allow_html=True
        )

# Scroll to latest message
st.markdown("<div id='bottom'></div>", unsafe_allow_html=True)
st.components.v1.html(
    "<script>document.getElementById('bottom').scrollIntoView();</script>",
    height=0
)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("⚖ Developed by Team BroCode — MIT ADT University")
