import streamlit as st
import bcrypt
import json
import os
from datetime import datetime
from functions import (
    get_bot_response, handle_example_query, login_form, signup_form,
    save_user_data, get_timestamp, load_user_data, hash_password
)

# ------------- CONFIG & CONSTANTS -------------
USER_DB_PATH = "user_data.json"

# ------------- APP INITIALIZATION -------------
def initialize_app():
    """Initialize the application configuration and session state."""
    st.set_page_config(
        page_title="MATBOT - MATLAB Assistant",
        page_icon="🧮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # load users
    if 'user_data' not in st.session_state:
        st.session_state.user_data = load_user_data()

    # auth flags
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"
        
    # per‐user sessions & settings
    if st.session_state.logged_in:
        user = st.session_state.username
        # load saved theme
        theme = st.session_state.user_data[user]["settings"].get("theme", "light")
        st.session_state.theme = theme
        # load saved chat sessions
        sessions = st.session_state.user_data[user].get("sessions", {"Chat 1": []})
        st.session_state.sessions = sessions
        # Set current session to the first one if not set
        if 'current_session' not in st.session_state:
            st.session_state.current_session = list(sessions.keys())[0]
    else:
        # Guest defaults
        if 'theme' not in st.session_state:
            st.session_state.theme = "light"
        if 'sessions' not in st.session_state:
            st.session_state.sessions = {"Chat 1": []}
        if 'current_session' not in st.session_state:
            st.session_state.current_session = "Chat 1"

    apply_matlab_theme(st.session_state.theme)

# ------------- UI COMPONENTS -------------
def render_sidebar():
    """Render GPT-like chat session list and controls, with delete support."""
    with st.sidebar:
        st.markdown("## 💬 Chats")
        # ➕ New Chat
        if st.button("➕ New Chat", use_container_width=True):
            idx = len(st.session_state.sessions) + 1
            name = f"Chat {idx}"
            st.session_state.sessions[name] = []
            st.session_state.current_session = name
            # Persist if logged in
            if st.session_state.logged_in:
                user = st.session_state.username
                st.session_state.user_data[user]['sessions'] = st.session_state.sessions
                save_user_data(st.session_state.user_data)
            st.rerun()

        # Session selector - with error handling
        sessions = list(st.session_state.sessions.keys())
        
        # Safety check - if current_session isn't in the list, default to first session
        if not sessions:
            # If no sessions exist, create one
            st.session_state.sessions["Chat 1"] = []
            st.session_state.current_session = "Chat 1"
            sessions = ["Chat 1"]
        elif st.session_state.current_session not in sessions:
            # If current_session doesn't exist in sessions, set to first available
            st.session_state.current_session = sessions[0]
            
        # Now we can safely get the index
        current_idx = sessions.index(st.session_state.current_session)
        sel = st.radio("Select a Chat", sessions, index=current_idx)
        
        if sel != st.session_state.current_session:
            st.session_state.current_session = sel
            st.rerun()

        # 🗑️ Delete Current Chat
        if st.button("🗑️ Delete Chat", use_container_width=True):
            if len(sessions) > 1:
                # Remove the selected chat
                st.session_state.sessions.pop(st.session_state.current_session)
                # Pick the first remaining session
                st.session_state.current_session = list(st.session_state.sessions.keys())[0]
                # Persist if logged in
                if st.session_state.logged_in:
                    user = st.session_state.username
                    st.session_state.user_data[user]['sessions'] = st.session_state.sessions
                    save_user_data(st.session_state.user_data)
                st.rerun()
            else:
                st.warning("Cannot delete the only remaining chat.")

        st.markdown("---")
        # Other sidebar items...
        st.markdown("## 📚 Resources")
        with st.expander("MATLAB Links", expanded=False):
            st.markdown("""
            - [Documentation](https://www.mathworks.com/help/matlab/)
            - [MATLAB Answers](https://www.mathworks.com/matlabcentral/answers/)
            """)
        st.markdown("---")
        st.caption("© 2025 MATBOT v1.0")

def render_navbar():
    """Render the top navigation bar with theme toggle and user login/logout."""
    navbar_container = st.container()
    with navbar_container:
        col1, col2, col3 = st.columns([4, 2, 2])
        with col2:
            current_theme = "🌙" if st.session_state.theme == "light" else "☀️"
            theme_label = "Dark Mode" if st.session_state.theme == "light" else "Light Mode"
            if st.button(f"{current_theme} {theme_label}", key="theme_toggle_nav"):
                change_theme("dark" if st.session_state.theme == "light" else "light")
        with col3:
            if st.session_state.logged_in:
                logout_col1, logout_col2 = st.columns([1.5, 2])
                with logout_col1:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
                        <div style="width: 24px; height: 24px; border-radius: 50%; background-color: var(--matlab-blue);
                                color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                            {st.session_state.username[0].upper()}
                        </div>
                        <span>{st.session_state.username}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with logout_col2:
                    if st.button("Logout", key="logout_button", use_container_width=True):
                        logout_user()
            else:
                login_col1, login_col2 = st.columns([1, 1])
                with login_col1:
                    if st.button("Login", key="login_nav_button"):
                        st.session_state.auth_page = "login"
                        st.rerun()
                with login_col2:
                    if st.button("Sign Up", key="signup_nav_button"):
                        st.session_state.auth_page = "signup"
                        st.rerun()
    st.markdown("---")

def render_chat_interface():
    """Render the main chat interface for a logged in user."""
    st.markdown(f"""
    <div class="logo-container">
        <h1>Welcome, {st.session_state.username}! 👋</h1>
        <p>I'm your MATLAB Troubleshooter assistant. How can I help you today?</p>
    </div>
    """, unsafe_allow_html=True)

    render_chat_history()
        
    render_chat_input()


def render_auth_interface():
    """Render the authentication interface."""
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    auth_col1, auth_col2 = st.columns([2, 3])
    with auth_col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/21/Matlab_Logo.png", width=150)
        st.markdown("### Welcome to MATBOT")
        st.markdown("""
        Your professional assistant for MATLAB:
        - Get instant help with syntax
        - Debug errors efficiently
        - Learn best practices
        - Optimize your code
        """)
    with auth_col2:
        if st.session_state.auth_page == "login":
            login_form()
        else:
            signup_form()
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_history():
    """Render messages for the currently selected chat only."""
    # Explicitly get the current session name
    current_session = st.session_state.current_session
    
    # Get messages for this specific chat only
    if current_session in st.session_state.sessions:
        messages = st.session_state.sessions[current_session]
    else:
        messages = []  # Fallback if session doesn't exist
    
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Show welcome message if this chat is empty
        if not messages:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="avatar bot-avatar">M</div>
                <div class="message-content">
                    <p>👋 Welcome to chat "{current_session}"! How can I help with your MATLAB questions?</p>
                    <div class="chat-timestamp">{get_timestamp()}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display all messages for this chat
        for message in messages:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="avatar user-avatar">U</div>
                    <div class="message-content">
                        <p>{message['content']}</p>
                        <div class="chat-timestamp">{message['timestamp']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <div class="avatar bot-avatar">M</div>
                    <div class="message-content">
                        {message['content']}
                        <div class="chat-timestamp">{message['timestamp']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_history():
    """Render messages for the current GPT-like session."""
    current_session = st.session_state.current_session
    msgs = st.session_state.sessions.get(current_session, [])
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if not msgs:
            st.markdown(f"""
            <div class="chat-message bot-message">
              <div class="avatar bot-avatar">M</div>
              <div class="message-content">
                <p>👋 Welcome to MATBOT! Ask me anything about MATLAB.</p>
                <div class="chat-timestamp">{get_timestamp()}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        for m in msgs:
            if m['role'] == 'user':
                cls = 'user-message'
                av = 'U'
            else:
                cls = 'bot-message'
                av = 'M'
            st.markdown(f"""
            <div class="chat-message {cls}">
              <div class="avatar {cls.split('-')[0]}-avatar">{av}</div>
              <div class="message-content">
                <p>{m['content']}</p>
                <div class="chat-timestamp">{m['timestamp']}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_input():
    """Render the chat input area using a Streamlit form."""
    st.markdown("### Ask Your Question")
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your MATLAB question here:",
            key="user_input",
            placeholder="E.g., How do I solve linear equations in MATLAB?",
            height=100
        )

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            uploaded_file = st.file_uploader("Attach file", type=["m", "mat"])

        with col3:
            # Create a large styled button using HTML and CSS
            submit_btn = st.form_submit_button(
                label="Send",
                use_container_width=True  # Uses full width of column
            )
            # Add a little space
            st.markdown(
                """<style>
                div.stButton > button:first-child {
                    font-size: 18px;
                    padding: 10px 24px;
                    border-radius: 8px;
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }
                </style>""",
                unsafe_allow_html=True
            )

    if submit_btn and user_input.strip():
        process_user_input(user_input)

    if uploaded_file is not None:
        file_details = {
            "Filename": uploaded_file.name,
            "Size": f"{uploaded_file.size/1024:.1f} KB"
        }
        st.success("File uploaded successfully!")


# ------------- STYLING FUNCTIONS -------------
def apply_matlab_theme(theme_mode):
    """Apply MATLAB-inspired theme with dark/light mode support."""
    if theme_mode == "dark":
        matlab_theme_css = """
        <style>
            :root {
                --matlab-blue: #0097E6;
                --matlab-orange: #FF8C42;
                --matlab-dark: #1E1E1E;
                --matlab-light: #333333;
                --matlab-code-bg: #2D2D2D;
                --text-color: #E0E0E0;
                --text-secondary: #B0B0B0;
                --border-color: #444444;
                --user-message-bg: #2C3E50;
                --bot-message-bg: #343434;
                --hover-color: #005685;
                --header-bg: #212121;
                --input-bg: #3D3D3D;
                --input-text: #FFFFFF;
                --input-border: #555555;
                --button-bg: #0097E6;
                --button-hover: #00B4F0;
                --navbar-bg: #151515;
            }
        """
    else:
        matlab_theme_css = """
            <style>
                :root {
                    /* MATLAB Light Theme Colors */
                    --matlab-blue: #0076A8;
                    --matlab-blue-light: #0096D6;
                    --matlab-orange: #E76500;
                    --matlab-orange-dark: #C55A00;
                    --matlab-light: #F7F7F7;
                    --matlab-code-bg: #F5F7F9;
                    --text-color: #222222;
                    --text-secondary: #444444;
                    --border-color: #CCCCCC;
                    --user-message-bg: #E1F0FA;
                    --bot-message-bg: #FFFFFF;
                    --hover-color: #005685;
                    --header-bg: #F0F0F0;
                    --input-bg: #FFFFFF;
                    --input-text: #222222;
                    --input-border: #BBBBBB;
                    --button-bg: #0076A8;
                    --button-hover: #0096D6;
                    --navbar-bg: #F0F0F0;
                }
            """
    common_css = """
        <style>
            /* Base styling */
            .stApp {
                background-color: var(--matlab-light);
            }
            
            h1, h2, h3 {
                color: var(--matlab-blue);
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
            }
            
            /* Chat messages */
            .chat-message {
                padding: 1.2rem;
                border-radius: 10px;
                margin-bottom: 1.2rem;
                display: flex;
                align-items: flex-start;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                animation: fadeIn 0.3s ease-in;
                color: var(--text-color);
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .user-message {
                background-color: var(--user-message-bg);
                border-left: 5px solid var(--matlab-blue);
            }
            
            .bot-message {
                background-color: var(--bot-message-bg);
                border-left: 5px solid var(--matlab-orange);
            }
            
            .message-content {
                flex-grow: 1;
                color: var(--text-color);
            }
            
            .message-content p {
                color: var(--text-color);
                margin-top: 0;
            }
            
            pre {
                background-color: var(--matlab-code-bg);
                padding: 1rem;
                border-radius: 8px;
                border-left: 3px solid var(--matlab-orange);
                font-family: 'Consolas', 'Courier New', monospace;
                white-space: pre-wrap;
                overflow-x: auto;
                color: var(--text-color);
                margin: 1rem 0;
            }
            
            code {
                color: var(--matlab-orange);
                background-color: var(--matlab-code-bg);
                padding: 0.2rem 0.4rem;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 0.9em;
            }
            
            /* Rest of your CSS */
            .stButton button {
                background-color: var(--button-bg);
                color: white;
                border-radius: 8px;
                border: none;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                transition: all 0.2s ease;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.9rem;
            }
            
            .stButton button:hover {
                background-color: var(--button-hover);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                transform: translateY(-1px);
            }
            
            .stTextInput div[data-baseweb="input"], 
            .stTextArea textarea {
                border-radius: 10px;
                border: 2px solid var(--input-border);
                background-color: var(--input-bg);
                transition: all 0.2s ease;
                color: var(--input-text);
            }
            
            .stTextInput input {
                color: var(--input-text);
            }
            
            .stTextInput div[data-baseweb="input"]:focus-within {
                border: 2px solid var(--matlab-blue);
                box-shadow: 0 0 0 2px rgba(0,118,168,0.2);
            }
            
            [data-testid="stSidebar"] {
                background-color: var(--matlab-dark);
                padding: 2rem 1rem;
            }
            
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {
                color: white;
            }
            
            [data-testid="stSidebar"] .stMarkdown p {
                color: #E0E0E0;
            }
            
            [data-testid="stSidebar"] a {
                color: var(--matlab-orange);
            }
            
            [data-testid="stSidebar"] a:hover {
                color: #FFB07C;
                text-decoration: underline;
            }
            
            .chat-timestamp {
                font-size: 0.8rem;
                color: var(--text-secondary);
                text-align: right;
                margin-top: 0.4rem;
                font-style: italic;
            }
            
            .avatar {
                width: 45px;
                height: 45px;
                border-radius: 50%;
                margin-right: 1rem;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .user-avatar {
                background-color: var(--matlab-blue);
            }
            
            .bot-avatar {
                background-color: var(--matlab-orange);
            }
            
            .logo-container {
                text-align: center;
                margin-bottom: 2rem;
                padding: 1.5rem;
                background-color: var(--header-bg);
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                color: var(--text-color);
            }
            
            .logo-container h1 {
                color: var(--matlab-blue);
            }
            
            .logo-container p {
                color: var(--text-color);
            }
            
            /* Other styles remain unchanged */
            /* ... */
        </style>
    """
    st.markdown(matlab_theme_css + common_css, unsafe_allow_html=True)


# ------------- ACTION HANDLERS -------------
def process_user_input(user_input):
    """Process user input and add to the CURRENT selected chat only."""
    # Get current chat
    current_session = st.session_state.current_session
    
    # Add message to the CURRENT chat only
    if current_session not in st.session_state.sessions:
        st.session_state.sessions[current_session] = []
    
    st.session_state.sessions[current_session].append({
        'role': 'user',
        'content': user_input,
        'timestamp': get_timestamp()
    })
    
    with st.spinner("MATLAB Troubleshooter is thinking..."):
        bot_response = get_bot_response(user_input)
        st.session_state.sessions[current_session].append({
            'role': 'assistant',
            'content': bot_response,
            'timestamp': get_timestamp()
        })
    
    # Save user data if logged in
    if st.session_state.logged_in:
        user = st.session_state.username
        st.session_state.user_data[user]['sessions'] = st.session_state.sessions
        save_user_data(st.session_state.user_data)
    
    st.rerun()

def new_chat():
    """Start a fresh chat, persist if logged-in."""
    idx = len(st.session_state.sessions) + 1
    name = f"Chat {idx}"
    st.session_state.sessions[name] = []
    st.session_state.current_session = name
    if st.session_state.logged_in:
        user = st.session_state.username
        st.session_state.user_data[user]['sessions'] = st.session_state.sessions
        save_user_data(st.session_state.user_data)
    st.rerun()

def clear_chat_history():
    """Clear current session’s history, persist if logged-in."""
    st.session_state.sessions[st.session_state.current_session] = []
    if st.session_state.logged_in:
        user = st.session_state.username
        st.session_state.user_data[user]['sessions'] = st.session_state.sessions
        save_user_data(st.session_state.user_data)
    st.rerun()

def change_theme(theme):
    """Change theme and persist per-user preference."""
    st.session_state.theme = theme
    if st.session_state.logged_in:
        user = st.session_state.username
        st.session_state.user_data[user]["settings"]["theme"] = theme
        save_user_data(st.session_state.user_data)
    st.rerun()
    
def logout_user():
    """Log out the current user."""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ------------- MAIN APP EXECUTION -------------
def main():
    """Main application entry point."""
    initialize_app()
    render_sidebar()
    render_navbar()
    if not st.session_state.logged_in:
        render_auth_interface()
    else:
        render_chat_interface()

if __name__ == "__main__":
    main()