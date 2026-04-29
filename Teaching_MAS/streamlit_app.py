import os
import streamlit as st
import uuid
import time
# from teacher import teacher_agent
from synthesize import workflow

# ================================================================
# PAGE CONFIG
# ================================================================

st.set_page_config(
    page_title="Academic AI System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# CUSTOM CSS
# ================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #13161f;
    --border:   #1e2330;
    --accent:   #4f8ef7;
    --accent2:  #a78bfa;
    --green:    #34d399;
    --yellow:   #fbbf24;
    --red:      #f87171;
    --text:     #e2e8f0;
    --muted:    #64748b;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'Sora', sans-serif;
    color: var(--text);
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Header */
.header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 0 24px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.header-icon {
    font-size: 2.2rem;
    background: linear-gradient(135deg, #4f8ef7, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header-title {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4f8ef7, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.header-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin: 0;
}

/* Chat messages */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 12px 0;
}
.msg-user .bubble {
    background: linear-gradient(135deg, #4f8ef7, #3b6fd4);
    color: #fff;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%;
    font-size: 0.93rem;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(79,142,247,0.25);
}

.msg-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 12px 0;
    gap: 10px;
}
.msg-assistant .avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a78bfa, #4f8ef7);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.msg-assistant .bubble {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 14px 18px;
    border-radius: 4px 18px 18px 18px;
    max-width: 75%;
    font-size: 0.93rem;
    line-height: 1.7;
}

/* Agent badge */
.agent-badge {
    display: inline-block;
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
    font-weight: 500;
}
.badge-teacher        { background: rgba(79,142,247,0.15); color: #4f8ef7; border: 1px solid rgba(79,142,247,0.3); }
.badge-teacher_assistant { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }
.badge-planner        { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-router         { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }

/* Status indicators */
.status-bar {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 8px 0 16px 0;
}
.status-dot {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.75rem;
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
}
.dot { width: 7px; height: 7px; border-radius: 50%; }
.dot-active  { background: var(--green); box-shadow: 0 0 6px var(--green); animation: pulse 1.5s infinite; }
.dot-idle    { background: var(--muted); }
.dot-routing { background: var(--yellow); box-shadow: 0 0 6px var(--yellow); animation: pulse 1s infinite; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* Thinking indicator */
.thinking {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--muted);
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 10px 0;
}
.thinking-dots span {
    display: inline-block;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--accent);
    animation: bounce 1.2s infinite;
    margin: 0 2px;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40%            { transform: translateY(-6px); }
}

/* Sidebar session item */
.session-item {
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
    margin-bottom: 6px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.82rem;
}
.session-item:hover  { border-color: var(--accent); background: rgba(79,142,247,0.07); }
.session-active { border-color: var(--accent) !important; background: rgba(79,142,247,0.12) !important; }

/* Input area */
[data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,0.2) !important;
}

/* Metrics */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.metric-val  { font-size: 1.6rem; font-weight: 700; color: var(--accent); }
.metric-label { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }

/* Divider */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ================================================================
# SESSION STATE INIT
# ================================================================

if "sessions" not in st.session_state:
    st.session_state.sessions = {}          # {session_id: {"name": str, "messages": []}}

if "active_session" not in st.session_state:
    # create default session
    sid = str(uuid.uuid4())[:8]
    st.session_state.sessions[sid] = {"name": "Session 1", "messages": []}
    st.session_state.active_session = sid

if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0


# ================================================================
# HELPERS
# ================================================================

def get_active_messages():
    return st.session_state.sessions[st.session_state.active_session]["messages"]

def add_message(role: str, content: str, agent: str = None):
    get_active_messages().append({
        "role":    role,
        "content": content,
        "agent":   agent,
        "time":    time.strftime("%H:%M"),
    })

def new_session():
    sid  = str(uuid.uuid4())[:8]
    name = f"Session {len(st.session_state.sessions) + 1}"
    st.session_state.sessions[sid] = {"name": name, "messages": []}
    st.session_state.active_session = sid

def clear_session():
    st.session_state.sessions[st.session_state.active_session]["messages"] = []

def render_message(msg: dict):
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="bubble">{msg['content']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        agent = msg.get("agent", "system")
        badge_class = f"badge-{agent}" if agent in ["teacher","teacher_assistant","planner","router"] else "badge-router"
        agent_label = {
            "teacher":           "🧑‍🏫 Teacher",
            "teacher_assistant": "🤝 Assistant",
            "planner":           "📋 Planner",
            "router":            "🧭 Router",
        }.get(agent, "🤖 Agent")

        st.markdown(f"""
        <div class="msg-assistant">
            <div class="avatar">🎓</div>
            <div>
                <span class="agent-badge {badge_class}">{agent_label}</span>
                <div class="bubble">{msg['content']}</div>
                <div style="font-size:0.68rem;color:var(--muted);margin-top:4px;font-family:'JetBrains Mono',monospace;">{msg.get('time','')}</div>
            </div>
        </div>""", unsafe_allow_html=True)


def query_workflow(user_input: str) -> str:

    # ✅ build history from current session messages
    history = get_active_messages()
    
    # format history as conversation context
    history_text = ""
    for msg in history[:-1]:  # exclude the last user message (already in query)
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n\n"

    # ✅ inject history into query
    full_query = user_input
    if history_text:
        full_query = f"""Previous conversation:
{history_text}
Current question: {user_input}"""

    inputs = {
        "query":           full_query,   # ✅ query + history
        "classifications": [],
        "results":         [],
        "final_answer":    "",
    }

    thread_id = f"session_{st.session_state.active_session}"
    config    = {"configurable": {"thread_id": thread_id}}

    final_text = ""
    try:
        for chunk in workflow.stream(inputs, config=config, stream_mode="values"):
            if "final_answer" in chunk and chunk["final_answer"]:
                final_text = chunk["final_answer"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

    return final_text or "I could not generate a response. Please try again."


# def query_workflow(user_input: str) -> str:

#     # ✅ build history
#     history = get_active_messages()
#     history_text = ""
#     for msg in history[:-1]:
#         role = "User" if msg["role"] == "user" else "Assistant"
#         history_text += f"{role}: {msg['content']}\n\n"

#     full_query = user_input
#     if history_text:
#         full_query = f"""Previous conversation:
# {history_text}
# Current question: {user_input}"""

#     # ✅ استخدم teacher_agent مباشرة — مش workflow
#     thread_id = f"session_{st.session_state.active_session}"
#     config    = {"configurable": {"thread_id": thread_id}}

#     final_text = ""
#     try:
#         result = teacher_agent.invoke(
#             {"messages": [("user", full_query)]},
#             config=config
#         )

#         messages = result.get("messages", [])
#         for msg in reversed(messages):
#             if hasattr(msg, "content") and msg.content:
#                 if not hasattr(msg, "tool_calls") or not msg.tool_calls:
#                     final_text = msg.content
#                     break

#     except Exception as e:
#         return f"⚠️ Error: {str(e)}"

#     return final_text or "I could not generate a response. Please try again."

# ================================================================
# SIDEBAR
# ================================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px 0">
        <div style="font-size:1.1rem;font-weight:700;background:linear-gradient(90deg,#4f8ef7,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            🎓 Academic AI
        </div>
        <div style="font-size:0.72rem;color:var(--muted);margin-top:2px;">Multi-Agent System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── New session button ──
    if st.button("＋  New Session", use_container_width=True, type="primary"):
        new_session()
        st.rerun()

    st.markdown("<div style='font-size:0.72rem;color:var(--muted);margin:12px 0 6px 0;font-family:JetBrains Mono,monospace;'>SESSIONS</div>", unsafe_allow_html=True)

    # ── Session list ──
    for sid, sdata in st.session_state.sessions.items():
        is_active = sid == st.session_state.active_session
        msg_count = len(sdata["messages"])
        label     = f"{sdata['name']}  ·  {msg_count // 2} msg{'s' if msg_count != 2 else ''}"
        cls       = "session-item session-active" if is_active else "session-item"

        st.markdown(f'<div class="{cls}" id="sess_{sid}">{label}</div>', unsafe_allow_html=True)
        if st.button(sdata["name"], key=f"btn_{sid}", use_container_width=True,
                     help="Switch to this session"):
            st.session_state.active_session = sid
            st.rerun()

    st.markdown("---")

    # ── Agents status ──
    st.markdown("<div style='font-size:0.72rem;color:var(--muted);margin-bottom:8px;font-family:JetBrains Mono,monospace;'>AGENTS</div>", unsafe_allow_html=True)

    for agent_name, color, icon in [
        ("Teacher",           "#4f8ef7", "🧑‍🏫"),
        ("Teacher Assistant", "#a78bfa", "🤝"),
        ("Planner",           "#34d399", "📋"),
        ("Router",            "#fbbf24", "🧭"),
    ]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;
                    padding:6px 10px;border-radius:6px;margin-bottom:4px;
                    background:var(--surface);border:1px solid var(--border);">
            <div style="width:7px;height:7px;border-radius:50%;background:{color};"></div>
            <span style="font-size:0.78rem;">{icon} {agent_name}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Stats ──
    msgs      = get_active_messages()
    user_msgs = [m for m in msgs if m["role"] == "user"]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(user_msgs)}</div>
            <div class="metric-label">Queries</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(st.session_state.sessions)}</div>
            <div class="metric-label">Sessions</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️  Clear Chat", use_container_width=True):
        clear_session()
        st.rerun()


# ================================================================
# MAIN AREA
# ================================================================

st.markdown("""
<div class="header">
    <div class="header-icon">🎓</div>
    <div>
        <p class="header-title">Academic AI System</p>
        <p class="header-sub">3 specialized agents · Router · Synthesizer</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ──
messages = get_active_messages()

if not messages:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:var(--muted);">
        <div style="font-size:3rem;margin-bottom:12px;">🎓</div>
        <div style="font-size:1rem;font-weight:600;color:var(--text);margin-bottom:6px;">
            Ask anything academic
        </div>
        <div style="font-size:0.82rem;">
            Theory · Technical · Planning — the right agent will handle it
        </div>
        <div style="margin-top:24px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">
            <span style="background:var(--surface);border:1px solid var(--border);
                         padding:6px 14px;border-radius:20px;font-size:0.78rem;">
                💡 Explain transformers in deep learning
            </span>
            <span style="background:var(--surface);border:1px solid var(--border);
                         padding:6px 14px;border-radius:20px;font-size:0.78rem;">
                🛠️ Fix my PyTorch CUDA error
            </span>
            <span style="background:var(--surface);border:1px solid var(--border);
                         padding:6px 14px;border-radius:20px;font-size:0.78rem;">
                📋 Create a 3-month ML roadmap
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in messages:
        render_message(msg)

# ── Thinking indicator ──
thinking_placeholder = st.empty()

# ── Chat input ──
user_input = st.chat_input("Ask your question...")

if user_input:
    # Add user message
    add_message("user", user_input)
    st.session_state.total_queries += 1

    # Show thinking
    with thinking_placeholder:
        st.markdown("""
        <div class="thinking">
            🧭 Routing &amp; thinking
            <span class="thinking-dots">
                <span></span><span></span><span></span>
            </span>
        </div>""", unsafe_allow_html=True)

    # Get full response
    response = query_workflow(user_input)

    # Clear thinking
    thinking_placeholder.empty()

    # ✅ stream character by character in the UI
    stream_placeholder = st.empty()
    displayed = ""

    for char in response:
        displayed += char
        stream_placeholder.markdown(f"""
        <div class="msg-assistant">
            <div class="avatar">🎓</div>
            <div>
                <span class="agent-badge badge-teacher">🧑‍🏫 Teacher</span>
                <div class="bubble">{displayed}▌</div>
            </div>
        </div>""", unsafe_allow_html=True)
        time.sleep(0.008)   # ⚡ adjust speed — lower = faster

    # Final render without cursor
    stream_placeholder.markdown(f"""
    <div class="msg-assistant">
        <div class="avatar">🎓</div>
        <div>
            <span class="agent-badge badge-teacher">🧑‍🏫 Teacher</span>
            <div class="bubble">{displayed}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Save to history
    add_message("assistant", response, agent="teacher")

    st.rerun()