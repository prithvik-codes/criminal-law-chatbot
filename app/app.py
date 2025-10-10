import streamlit as st
import json
import os
import google.generativeai as genai

# ----------------------------
# CONFIGURE GOOGLE GEMINI API
# ----------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Use env variable for safety
MODEL_NAME = "gemini-2.5-flash"

# ----------------------------
# LOAD LOCAL LEGAL DATA
# ----------------------------
DATA_PATHS = [
    r"data/statutes.json",
    r"data/judgments.json",
]

legal_docs = []
for path in DATA_PATHS:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            legal_docs.extend(json.load(f))

# ----------------------------
# SESSION STATE INITIALIZATION
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rerun_needed" not in st.session_state:
    st.session_state.rerun_needed = False

# Handle safe rerun
if st.session_state.rerun_needed:
    st.session_state.rerun_needed = False
    st.experimental_rerun()

# ----------------------------
# STREAMLIT UI CONFIG
# ----------------------------
st.set_page_config(page_title="Criminal Law Chatbot", page_icon="⚖")
st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #1f2937;  /* dark blue-gray */
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        margin-left: auto;
        margin-bottom: 5px;
    }
    .bot-bubble {
        background-color: #374151;  /* dark gray */
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        margin-right: auto;
        margin-bottom: 5px;
    }
    .chat-container {
        overflow-y: auto;
        max-height: 500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚖ Criminal Law Chatbot")
st.caption("Ask questions about Indian Criminal Law, IPC sections, or legal case references.")

# ----------------------------
# USER INPUT
# ----------------------------
query = st.text_area(
    "Enter your legal question:",
    height=100,
    placeholder="e.g., What is Section 378 of IPC?",
    key="query_input"
)

if st.button("Send", key="send_button"):
    if query.strip():
        # Build context from local legal docs
        context_snippets = []
        for d in legal_docs:
            text = d.get("text", "")
            if query.lower() in text.lower():
                context_snippets.append(text)
        context = "\n".join(context_snippets[:5])

        prompt = f"""
You are an expert Indian criminal law assistant.
Use the following context from statutes and judgments (if relevant) to answer precisely.

Context:
{context or "No relevant context found in local data."}

Question:
{query}

Answer concisely in simple legal terms, citing IPC sections or examples where possible.
"""

        # Add user message
        st.session_state.messages.append({"role": "user", "text": query})

        # Generate response from Gemini
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            bot_text = response.text
        except Exception as e:
            bot_text = f"❌ Error generating response: {e}"

        st.session_state.messages.append({"role": "bot", "text": bot_text})

# ----------------------------
# DISPLAY CHAT
# ----------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# SIDEBAR - DELETE CHATS
# ----------------------------
st.sidebar.title("Chat Controls")
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        if st.sidebar.button(f"Delete chat {i+1}", key=f"del_{i}"):
            # Remove user + bot response
            to_delete = [i]
            if i+1 < len(st.session_state.messages) and st.session_state.messages[i+1]["role"] == "bot":
                to_delete.append(i+1)
            for idx in sorted(to_delete, reverse=True):
                st.session_state.messages.pop(idx)
            st.session_state.rerun_needed = True

st.sidebar.markdown("---")
if st.sidebar.button("Clear all chats"):
    st.session_state.messages = []
    st.session_state.rerun_needed = True

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("👨‍⚖ Developed by Team BroCode — MIT ADT University")
