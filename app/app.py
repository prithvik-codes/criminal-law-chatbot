import streamlit as st
import google.generativeai as genai
import json
import os

# ----------------------------
# CONFIGURE GOOGLE GEMINI API
# ----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # Replace with your Gemini API key
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
# STREAMLIT UI SETUP
# ----------------------------
st.set_page_config(page_title="Criminal Law Chatbot", page_icon="⚖", layout="wide")
st.markdown(
    """
    <style>
    /* Dark background */
    .stApp {background-color: #121212; color: white;}
    /* Text input dark mode */
    textarea, input {background-color: #1E1E1E; color: white;}
    /* Scrollbar for chat */
    div[data-baseweb="base-input"] {color:white;}
    </style>
    """, unsafe_allow_html=True
)

st.title("⚖ Criminal Law Chatbot")
st.caption("Ask questions about Indian Criminal Law, IPC sections, or legal case references.")

# ----------------------------
# SESSION STATE FOR MESSAGE HISTORY
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

messages = st.session_state.messages

# ----------------------------
# SIDEBAR CHAT MANAGEMENT
# ----------------------------
st.sidebar.title("🗂 Chat History")

# Display previous chats grouped by user-bot
# Each chat is a user message + next bot message
for i, msg in enumerate(messages):
    if msg["role"] == "user":
        with st.sidebar.expander(f"Chat {i//2 + 1}: {msg['text'][:30]}...", expanded=False):
            st.write("*User:*", msg["text"])
            if i + 1 < len(messages) and messages[i + 1]["role"] == "bot":
                st.write("*Bot:*", messages[i + 1]["text"])
            # Delete button
            if st.button("Delete this chat", key=f"del_{i}"):
                # Remove user + bot
                to_delete = [i]
                if i + 1 < len(messages) and messages[i + 1]["role"] == "bot":
                    to_delete.append(i + 1)
                for idx in sorted(to_delete, reverse=True):
                    messages.pop(idx)
                st.experimental_rerun()

# ----------------------------
# USER INPUT
# ----------------------------
query = st.text_area(
    "Enter your legal question:",
    height=100,
    placeholder="e.g., What is Section 378 of IPC?",
    key="query_input"
)

# Send button
if st.button("Send", key="send_button"):
    if query.strip():
        # Add user message
        messages.append({"role": "user", "text": query})

        # Build context from local docs
        context_snippets = []
        for d in legal_docs:
            text = d.get("text", "")
            if query.lower() in text.lower():
                context_snippets.append(text)
        context = "\n".join(context_snippets[:5])

        # Prepare prompt for Gemini
        prompt = f"""
You are an expert Indian criminal law assistant.
Use the following context from statutes and judgments (if relevant) to answer precisely.

Context:
{context or "No relevant context found in local data."}

Question:
{query}

Answer concisely in simple legal terms, citing IPC sections or examples where possible.
"""

        with st.spinner("Generating response..."):
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(prompt)
                bot_text = response.text.strip()
            except Exception as e:
                bot_text = f"❌ Error generating response: {e}"

        messages.append({"role": "bot", "text": bot_text})
        st.experimental_rerun()

# ----------------------------
# DISPLAY CHAT BUBBLES
# ----------------------------
chat_container = st.container()
with chat_container:
    for msg in messages[-50:]:  # last 50 messages
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style="
                    text-align:right;
                    background-color:#1E4620;
                    color:white;
                    border-radius:15px;
                    padding:10px;
                    margin:5px;
                    display:inline-block;
                    max-width:80%;
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
                    color:white;
                    border-radius:15px;
                    padding:10px;
                    margin:5px;
                    display:inline-block;
                    max-width:80%;
                    float:left;
                    clear:both;
                ">{msg['text']}</div>
                <div style="clear:both;"></div>
                """,
                unsafe_allow_html=True
            )

# ----------------------------
# AUTOSCROLL TO LATEST MESSAGE
# ----------------------------
scroll_anchor = st.empty()
scroll_anchor.markdown(
    "<div id='scroll_anchor'></div><script>var el=document.getElementById('scroll_anchor'); el.scrollIntoView({behavior:'smooth'});</script>",
    unsafe_allow_html=True
)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("👨‍⚖ Developed by Team BroCode")
