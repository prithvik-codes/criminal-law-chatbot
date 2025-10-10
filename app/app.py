# app.py
import streamlit as st
import google.generativeai as genai
import json
import os

# ----------------------------
# CONFIGURE GOOGLE GEMINI API
# ----------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Load from environment variable
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
# INITIALIZE SESSION STATE
# ----------------------------
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = [{"name": "New Chat", "messages": []}]
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = 0

# ----------------------------
# STREAMLIT PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Criminal Law Chatbot", page_icon="⚖", layout="wide")
st.title("⚖ Criminal Law Chatbot")
st.caption("Ask questions about Indian Criminal Law, IPC sections, or case judgments.")

# ----------------------------
# SIDEBAR: CHAT SESSIONS
# ----------------------------
with st.sidebar:
    st.header("💬 Your Chats")
    chat_names = [c["name"] for c in st.session_state["chat_sessions"]]
    choice = st.selectbox("Switch Chat:", chat_names, index=st.session_state["current_chat"])
    st.session_state["current_chat"] = chat_names.index(choice)

    if st.button("➕ New Chat"):
        st.session_state["chat_sessions"].append({"name": f"New Chat {len(chat_names)+1}", "messages": []})
        st.session_state["current_chat"] = len(st.session_state["chat_sessions"]) - 1
        st.experimental_rerun()

    if st.button("🗑 Clear Current Chat"):
        st.session_state["chat_sessions"][st.session_state["current_chat"]]["messages"] = []
        st.experimental_rerun()

# ----------------------------
# DISPLAY CHAT MESSAGES
# ----------------------------
chat_container = st.container()
messages = st.session_state["chat_sessions"][st.session_state["current_chat"]]["messages"]

with chat_container:
    for msg in messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div style="text-align:right; background-color:#DCF8C6; padding:10px; border-radius:12px; margin:5px; max-width:70%; float:right; clear:both;">{msg["text"]}</div>',
                unsafe_allow_html=True
            )
        else:  # bot
            st.markdown(
                f'<div style="text-align:left; background-color:#F1F0F0; padding:10px; border-radius:12px; margin:5px; max-width:70%; float:left; clear:both;">{msg["text"]}</div>',
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)  # spacing at bottom

# ----------------------------
# USER INPUT
# ----------------------------
user_input = st.text_area("Type your question here:", height=100, key="query_input")
if st.button("Send"):
    if user_input.strip():
        # Add user message
        messages.append({"role": "user", "text": user_input})

        # ----------------------------
        # OPTIONAL: build context from local statutes/judgments
        # ----------------------------
        context_snippets = []
        for d in legal_docs:
            text = d.get("text", "")
            if user_input.lower() in text.lower():
                context_snippets.append(text)
        context = "\n".join(context_snippets[:5])

        # ----------------------------
        # GENERATE BOT RESPONSE USING GEMINI
        # ----------------------------
        prompt = f"""
You are an expert Indian criminal law assistant.
Use the following context from statutes and judgments (if relevant) to answer precisely.

Context:
{context or "No relevant context found in local data."}

Question:
{user_input}

Answer concisely in simple legal terms, citing IPC sections or examples where possible.
"""
        with st.spinner("Generating response..."):
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(prompt)
                bot_text = response.text
            except Exception as e:
                bot_text = f"❌ Error generating response: {str(e)}"

        # Add bot message
        messages.append({"role": "bot", "text": bot_text})
        st.experimental_rerun()

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("👨‍⚖ Developed by Team BroCode — Criminal Law Chatbot")
