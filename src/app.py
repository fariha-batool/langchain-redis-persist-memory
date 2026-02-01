import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from memory.redis_memory import RedisMemoryChat
from src.config import settings

load_dotenv()

svg_path = Path(__file__).parent / "ui" / "redis_illustration.svg"
svg_html = svg_path.read_text(encoding="utf-8")

# Then in ui.html, replace <img ...> with a placeholder comment,
# and after st.markdown(ui_html, ...) do:

# Page config
st.set_page_config(
    page_title="Redis Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Session state init
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

# Load external HTML/CSS
UI_PATH = Path(__file__).parent / "ui" / "ui.html"
if UI_PATH.exists():
    ui_html = UI_PATH.read_text(encoding="utf-8")
    st.markdown(ui_html, unsafe_allow_html=True)
else:
    st.warning("UI template not found. Make sure `src/ui/ui.html` exists.")

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Session</div>', unsafe_allow_html=True)

    session_id = st.text_input(
        "Session ID",
        "user_001",
        help="Unique identifier for your chat session",
        key="session_input",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Advanced
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Connection</div>', unsafe_allow_html=True)

    redis_url = st.text_input(
        "Redis URL",
        os.getenv("REDIS_URL", settings.redis_url),
        help="Redis connection URL",
    )
    ttl_hours = st.slider("TTL (hours)", 0, 720, 24)
    ttl = ttl_hours * 3600 if ttl_hours > 0 else None

    # Init chat engine
    if st.session_state.chat_engine is None:
        st.session_state.chat_engine = RedisMemoryChat(
            redis_url=redis_url,
            ttl=ttl,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Stats</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("UI Messages", len(st.session_state.ui_messages))
    with col2:
        try:
            count = st.session_state.chat_engine.get_message_count(session_id)
            st.metric("Stored", count)
        except Exception:
            st.metric("Stored", "N/A")

    st.markdown("</div>", unsafe_allow_html=True)

    # Clear
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    if st.button("Clear history", use_container_width=True):
        try:
            st.session_state.chat_engine.clear_session(session_id)
        except Exception:
            pass
        st.session_state.ui_messages = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


history_container = st.container()

with history_container:
    if st.session_state.ui_messages:
        for message in st.session_state.ui_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else:
        st.markdown(
            """
            <div class="chat-empty">
              <h3>Start a new conversation</h3>
              <p>Ask anything. This session will be remembered in Redis.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

prompt = st.chat_input("Message Redis Chat…")

if prompt:
    st.session_state.ui_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                response = st.session_state.chat_engine.chat(prompt, session_id)
                st.markdown(response)
                st.session_state.ui_messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Check your Redis connection in the sidebar.")

