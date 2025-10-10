import streamlit as st
import google.generativeai as genai
import json
import os

# ----------------------------
# CONFIGURE GOOGLE GEMINI API
# ----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # store your API key in .streamlit/secrets.toml
MODEL_NAME = "gemini-2.5-flash"

# ----------------------------
# LOAD LOCAL LEGAL DATA
# ----------------------------
DATA_PATHS = ["data/statutes.json", "data/judgments.json"]
legal_docs = []
for path in DATA_PATHS:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            legal_docs.extend(json.load(f))

# ----------------------------
# STREAMLIT UI CONFIG
# ----------------------------
st.set_page_config(page_title="Criminal Law Chatbot", page_icon="⚖", layout="wide")
st.title("⚖ Criminal Law Chatbot")
st.caption("Ask questions about Indian Criminal Law, IPC sections, or legal case references.")

# ----------------------------
# SESSION STATE FOR CHAT
# ----------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ----------------------------
# SIDEBAR: Suggested Questions & Reset
# ----------------------------
with st.sidebar:
    st.header("⚖ Quick Actions")
    if st.button("Reset Chat"):
        st.session_state["messages"] = []


# ----------------------------
# USER INPUT
# ----------------------------
query = st.text_area("Ask your legal question:", height=100, key="query_input")
if st.button("Send"):
    if query.strip():
        # Add user message to session
        st.session_state["messages"].append({"role": "user", "text": query})

        # ----------------------------
        # BUILD CONTEXT FROM LOCAL DATA
        # ----------------------------
        context_snippets = [
            d.get("text", "") for d in legal_docs
            if query.lower() in d.get("text", "").lower()
        ]
        context = "\n".join(context_snippets[:3])  # top 3 matches

        # ----------------------------
        # BUILD PROMPT FOR GEMINI
        # ----------------------------
        chat_history = ""
        for msg in st.session_state["messages"][-6:]:  # last 6 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            chat_history += f"{role}: {msg['text']}\n"

        prompt = f"""
You are an expert Indian criminal law assistant.
Use the following context from statutes and judgments (if relevant) to answer accurately.

Context:
{context or "No relevant context found."}

Conversation so far:
{chat_history}

Answer the user's latest question concisely, in simple legal terms, citing IPC sections or examples where possible.
"""

        # ----------------------------
        # GENERATE RESPONSE
        # ----------------------------
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = "⚠ Error generating response. Please try again."

        st.session_state["messages"].append({"role": "assistant", "text": answer})

# ----------------------------
# DISPLAY CHAT HISTORY AS BUBBLES
# ----------------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["text"])
    else:
        st.chat_message("assistant").write(msg["text"])

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("👨‍⚖ Developed by Team BroCode — MIT ADT University")
