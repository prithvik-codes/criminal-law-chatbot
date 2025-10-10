import streamlit as st
import google.generativeai as genai
import json
import os

# ----------------------------
# CONFIGURE GOOGLE GEMINI API
# ----------------------------
genai.configure(api_key= "GEMINI_API_KEY")  # Replace with your real Gemini API key
MODEL_NAME = "gemini-2.0-flash"

# ----------------------------
# LOAD LOCAL LEGAL DATA
# ----------------------------
DATA_PATHS = [
    r"C:\Users\Prithviraj\crminal-law-chatbot\data\statutes.json",
    r"C:\Users\Prithviraj\crminal-law-chatbot\data\judgments.json",
]

legal_docs = []
for path in DATA_PATHS:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            legal_docs.extend(json.load(f))

# ----------------------------
# STREAMLIT UI
# ----------------------------
st.set_page_config(page_title="Criminal Law Chatbot", page_icon="⚖️")
st.title("⚖️ Criminal Law Chatbot")
st.caption("Ask questions about Indian Criminal Law, IPC sections, or legal case references.")

# ----------------------------
# USER INPUT
# ----------------------------
query = st.text_area(
    "🔍 Enter your legal question:",
    height=100,
    placeholder="e.g., What is Section 378 of IPC?",
    key="query_input"
)

# Button with unique key to prevent duplicate ID error
if st.button("Get Answer", key="get_answer_button"):
    if not query.strip():
        st.warning("Please enter a question before clicking the button.")
    else:
        with st.spinner("Analyzing legal data and generating response..."):
            # Optional: build context from local statutes/judgments
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

            # Generate response using Google Gemini
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)

            st.subheader("📘 Answer:")
            st.write(response.text)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("👨‍⚖️ *Developed by Uss*")
