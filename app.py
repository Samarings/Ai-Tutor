import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # reads .env file automatically

# Custom CSS for gradient background
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #07273e, #030617);
}
.stSidebar {
    background-color: #030617 !important;
}
.stAppHeader {
    background-color: #07273e !important;
}
h1, h2, h3, p, div {
    color: #ffffff !important;
}
.stChatInput, .stChatInputContainer, .stBottom, .stTextInput {
    background-color: ##0e1118 !important;
}
.stChatInput input, .stTextInput input {
    background-color: #0e1118 !important;
    color: #ffffff !important;
}
.stChatInput input::placeholder, .stTextInput input::placeholder {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Tutor",
    page_icon="🎓",
    layout="centered",
)

# ── API Setup ─────────────────────────────────────────────────────────────────
API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    st.error("No API key found. Add PERPLEXITY_API_KEY to your .env file.")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.perplexity.ai"
)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a highly encouraging and effective AI Tutor. 
Your goal is to help the student understand concepts deeply, not just give away the answer.

Follow these rules:
- Be concise but warm.
- If a student asks a direct question, explain the "why" before giving the "what."
- Use Socratic questioning: ask the student a small follow-up question to check their understanding.
- Use real-world analogies to explain complex topics.
- Cite your sources using [1], [2] format based on the search results you find.
- If you are unsure about an answer, just say that you are unsure, do not lie. 
- Use the students own words from the conversation to make your explanations more relatable.
-You are a professional math tutor. 
-ALL math MUST ALWAYS be written in LaTeX syntax format NO MATTER WHAT, NO EXCEPTIONS, EVEN IN PRACTICE QUESTIONS, LONG EQUATIONS, OR EXPLANATIONS.
-Use $$ for display math.
-Use \\frac{}{} for fractions and \\superscript{} for powers.
-Do not EVER use formatting other than laTeX, it gets confusing for the students according to surveys. 
"""

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": ..., "content": ...}

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background-color: #07273e; color: white; padding: 20px; text-align: center;">
<h1>🎓 AI Tutor</h1>
<p>Powered by Perplexity Sonar · Ask me anything — I'll help you *understand*, not just memorize.</p>
</div>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components

# Replace YOUR_AD_SLOT_ID with the ad unit ID you create in AdSense
adsense_code = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4190493846324723"
     crossorigin="anonymous"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4190493846324723"
     data-ad-slot="YOUR_AD_SLOT_ID"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
components.html(adsense_code, height=200)


# Sidebar controls
with st.sidebar:
    st.header("Settings")
    model_choice = st.selectbox(
        "Model",
        ["sonar", "sonar-pro", "sonar-reasoning"],
        index=0,
        help="sonar-pro gives deeper answers; sonar-reasoning shows step-by-step logic."
    )
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("**Tips**")
    st.markdown("- Ask *why*, not just *what*")
    st.markdown("- Follow up if something is unclear")
    st.markdown("- Try 'Can you quiz me on this?'")
    st.markdown("- If asking your tutor for math help, tell it to use only laTeX format")

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask your tutor a question…"):
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build message list for the API
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    api_messages.extend(st.session_state.messages[:-1])  # history before current
    api_messages.append({"role": "user", "content": prompt})

    # Stream the tutor's response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        stream = client.chat.completions.create(
            model=model_choice,
            messages=api_messages,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
