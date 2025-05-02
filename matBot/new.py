import streamlit as st
import bcrypt
import json
import os
from datetime import datetime
from functions import get_bot_response, handle_example_query, login_form, signup_form, save_user_data, get_timestamp, load_user_data ,hash_password

# ------------- CONFIG & CONSTANTS -------------
USER_DB_PATH = "user_data.json"

# ------------- APP INITIALIZATION -------------
def initialize_app():
    """Initialize the application configuration and session state"""
    # Set page configuration
    st.set_page_config(
        page_title="MATBOT - MATLAB Assistant",
        page_icon="🧮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state variables
    if 'user_data' not in st.session_state:
        st.session_state.user_data = load_user_data()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"
    
    # Apply theme
    apply_matlab_theme(st.session_state.theme)

# ------------- DATA UTILITIES -------------


# ------------- UI COMPONENTS -------------
def render_sidebar():
    """Render the sidebar with app controls and resources"""
    with st.sidebar:
        # Logo and title
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://upload.wikimedia.org/wikipedia/commons/2/21/Matlab_Logo.png", width=60)
        with col2:
            st.markdown("### MATBOT")
            st.markdown("*MATLAB Assistant*")
     
        
        # User section
        if st.session_state.logged_in:

            # Chat controls
            st.subheader("💬 Chat Controls")
            if st.button("🔄 New Chat", use_container_width=True):
                new_chat()
            
            if st.button("🗑️ Clear History", use_container_width=True):
                clear_chat_history()
            
            
        
        # Resources section
        st.markdown("---")
        with st.expander("📚 MATLAB Resources", expanded=False):
            st.markdown("""
            - [📖 Documentation](https://www.mathworks.com/help/matlab/)
            - [💬 MATLAB Answers](https://www.mathworks.com/matlabcentral/answers/)
            - [🎓 Tutorials](https://www.mathworks.com/support/learn-with-matlab-tutorials.html)
            - [🔍 Function Search](https://www.mathworks.com/help/search.html)
            """)
        
        # About/footer
        st.markdown("---")
        st.caption("© 2025 MATBOT v1.0")
        st.caption("Powered by advanced RAG technology")

def render_navbar():
    """Render the top navigation bar"""
    # Container for better styling
    navbar_container = st.container()
    with navbar_container:
        col1, col2, col3 = st.columns([4, 2, 2])
        
        # Add theme toggle in the middle
        with col2:
            current_theme = "🌙" if st.session_state.theme == "light" else "☀️"
            theme_label = "Dark Mode" if st.session_state.theme == "light" else "Light Mode"
            # Hidden button to handle the click
            if st.button(f"{current_theme} {theme_label}", key="theme_toggle_nav"):
              change_theme("dark" if st.session_state.theme == "light" else "light")
        
        with col3:
            # User info or login buttons
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
                    # Increased width logout button
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

def render_auth_interface():
    """Render the authentication interface"""
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    
    # Two-column layout with image and form
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
        else:  # signup page
            signup_form()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_interface():
    """Render the main chat interface"""
    # Welcome header with personalized greeting 
    st.markdown(f"""
    <div class="logo-container">
        <h1>Welcome, {st.session_state.username}! 👋</h1>
        <p>I'm your MATLAB Troubleshooter assistant. How can I help you today?</p>
    </div>
    """, unsafe_allow_html=True)

    # Chat history display directly (removed quick examples section)
    render_chat_history()

    # File uploader with icon
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("""
        <div style="margin-top: 20px; text-align: center;">
            <div style="font-weight: bold; margin-bottom: 10px;">
                <span style="font-size: 1.2rem;">📄</span> Upload MATLAB File
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=["m", "mat"])
        if uploaded_file is not None:
            file_details = {"Filename": uploaded_file.name, "Size": f"{uploaded_file.size/1024:.1f} KB"}
            st.success(f"File uploaded successfully!")

    # User input area
    render_chat_input()

def render_chat_history():
    """Render the chat history container"""
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.conversation_started:
            # Welcome message
            st.markdown("""
            <div class="chat-message bot-message">
                <div class="avatar bot-avatar">M</div>
                <div class="message-content">
                    <p>👋 Welcome to the MATLAB Troubleshooter! I'm here to help with your MATLAB programming questions.</p>
                    <p>I can assist with:</p>
                    <ul>
                        <li>MATLAB syntax and functions</li>
                        <li>Debugging common errors</li>
                        <li>Optimization techniques</li>
                        <li>Data visualization</li>
                        <li>Simulink modeling</li>
                        <li>Best practices</li>
                    </ul>
                    <p>How can I help you today?</p>
                    <div class="chat-timestamp">""" + get_timestamp() + """</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.conversation_started = True
        
        # Display chat history
        for message in st.session_state.chat_history:
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

def render_chat_input():
    """Render the user input area for chat"""
    st.markdown("### Ask Your Question")
    
    # Create columns for input and send button
    input_col, button_col = st.columns([10, 1])
    
    # Input field with placeholder
    with input_col:
        user_input = st.text_area("Type your MATLAB question here:", 
                                key="user_input", 
                                placeholder="E.g., How do I solve linear equations in MATLAB?",
                                height=100)
    
    # Send button with up arrow icon
    with button_col:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        send_btn = st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <button id="send_button" style="background-color: var(--button-bg); border: none; border-radius: 50%; 
                    width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; 
                    cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: all 0.2s ease;" 
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.3)';" 
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 5px rgba(0,0,0,0.2)';"
                    onclick="document.getElementById('submit_button').click();">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" 
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 19V5M5 12l7-7 7 7"/>
                </svg>
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden submit button that's triggered by the custom button
        submit_btn = st.button("Submit", key="submit_button", on_click=None)
        st.markdown("""
        <style>
        #submit_button { display: none; }
        </style>
        """, unsafe_allow_html=True)
        
        # Add JavaScript to allow pressing Ctrl+Enter to submit
        st.markdown("""
        <script>
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                document.getElementById('submit_button').click();
            }
        });
        </script>
        """, unsafe_allow_html=True)
    
    # Process user input if submitted
    if submit_btn and user_input.strip():
        process_user_input(user_input)

# ------------- STYLING FUNCTIONS -------------
def apply_matlab_theme(theme_mode):
    """Apply MATLAB-inspired theme with dark/light mode support"""
    if theme_mode == "dark":
        matlab_theme_css = """
        <style>
            /* MATLAB-inspired colors - Dark Mode */
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
    else:  # Light mode
        matlab_theme_css = """
        <style>
            /* MATLAB-inspired colors - Light Mode */
            :root {
                --matlab-blue: #0076A8;
                --matlab-orange: #F28F3B;
                --matlab-dark: #243746;
                --matlab-light: #FFFFFF;
                --matlab-code-bg: #F5F7F9;
                --text-color: #333333;
                --text-secondary: #666666;
                --border-color: #E0E0E0;
                --user-message-bg: #E6F2F8;
                --bot-message-bg: #FFFFFF;
                --hover-color: #005685;
                --header-bg: #F8F9FB;
                --input-bg: #FFFFFF;
                --input-text: #333333;
                --input-border: #CCCCCC;
                --button-bg: #0076A8;
                --button-hover: #005685;
                --navbar-bg: #F0F0F0;
            }
        """
    
    # Common CSS for both themes
    common_css = """
        /* Page background */
        .stApp {
            background-color: var(--matlab-light);
            color: var(--text-color);
        }
        
        /* Header styling */
        h1, h2, h3 {
            color: var(--matlab-blue);
            font-family: 'Segoe UI', Arial, sans-serif;
            font-weight: 600;
        }
        
        /* Chat message containers */
        .chat-message {
            padding: 1.2rem;
            border-radius: 10px;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: flex-start;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            animation: fadeIn 0.3s ease-in;
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
        
        /* Code blocks */
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
        
        /* Button styling */
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
        
        /* Input box */
        .stTextInput div[data-baseweb="input"] {
            border-radius: 10px;
            border: 2px solid var(--input-border);
            background-color: var(--input-bg);
            transition: all 0.2s ease;
        }
        
        .stTextInput input {
            color: var(--input-text);
        }
        
        .stTextInput div[data-baseweb="input"]:focus-within {
            border: 2px solid var(--matlab-blue);
            box-shadow: 0 0 0 2px rgba(0,118,168,0.2);
        }
        
        /* Sidebar */
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
        
        /* Chat timestamp */
        .chat-timestamp {
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-align: right;
            margin-top: 0.4rem;
            font-style: italic;
        }
        
        /* Avatar styling */
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
        
        .message-content {
            flex-grow: 1;
            color: var(--text-color);
        }
        
        /* Logo container */
        .logo-container {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1.5rem;
            background-color: var(--header-bg);
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        /* Navbar styling */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 1.5rem;
            background-color: var(--navbar-bg);
            color: var(--text-color);
            border-radius: 8px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .navbar-logo {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        
        .navbar-logo img {
            height: 28px;
        }
        
        .navbar-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--matlab-blue);
            margin: 0;
        }
        
        .navbar-buttons {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .theme-toggle {
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            background-color: var(--matlab-dark);
            color: white;
            font-size: 0.8rem;
            transition: all 0.2s ease;
        }
        
        .theme-toggle:hover {
            background-color: var(--matlab-blue);
        }
        
        .navbar-button {
            background-color: var(--button-bg);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.3rem 0.8rem;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .navbar-button:hover {
            background-color: var(--button-hover);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .user-avatar-small {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background-color: var(--matlab-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        /* For lists inside chat messages */
        .message-content ul, .message-content ol {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            padding-left: 1.5rem;
        }
        
        .message-content li {
            margin-bottom: 0.3rem;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--matlab-light);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--matlab-blue);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--hover-color);
        }
        
        /* Button container */
        .button-container {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }
        
        /* Chat container */
        .chat-container {
            max-height: 600px;
            overflow-y: auto;
            padding-right: 10px;
            margin-bottom: 20px;
        }
        
        /* Resources in sidebar footer */
        .sidebar-footer {
            margin-top: auto;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.9rem;
            opacity: 0.9;
            position: absolute;
            bottom: 20px;
            width: calc(100% - 2rem);
        }
        
        .resource-link {
            display: block;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            text-decoration: none;
        }
        
        .resource-link:hover {
            color: var(--matlab-orange);
            text-decoration: underline;
        }
        
        /* Auth forms */
        .auth-form {
            background-color: var(--bot-message-bg);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            border-left: 5px solid var(--matlab-blue);
        }
        
        .auth-link {
            color: var(--matlab-blue);
            cursor: pointer;
            text-decoration: underline;
        }
        
        .auth-link:hover {
            color: var(--matlab-orange);
        }
        
        .auth-error {
            color: #e74c3c;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        /* Loading animation for bot response */
        @keyframes pulseAnimation {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .typing-indicator {
            display: flex;
            padding: 0.5rem 1rem;
            background-color: var(--bot-message-bg);
            border-radius: 20px;
            width: fit-content;
            margin-bottom: 1rem;
            animation: pulseAnimation 1.5s infinite;
        }
        
        .typing-indicator span {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            background-color: var(--matlab-blue);
            margin: 0 2px;
            display: inline-block;
        }
        
        .typing-indicator span:nth-child(1) {
            animation: blink 1s infinite 0.2s;
        }
        
        .typing-indicator span:nth-child(2) {
            animation: blink 1s infinite 0.4s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation: blink 1s infinite 0.6s;
        }
        
        @keyframes blink {
            50% { opacity: 0; }
        }
        
        [data-testid="stFileUploadDropzone"] {
            background-color: var(--bot-message-bg) !important;
            border-color: var(--border-color) !important;
            color: var(--text-color) !important;
        }
    </style>
    """
    
    st.markdown(matlab_theme_css + common_css, unsafe_allow_html=True)

# ------------- ACTION HANDLERS -------------
def process_user_input(user_input):
    """Process user input and generate response"""
    # Add user message to chat history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': get_timestamp()
    })
    
    # Show typing indicator
    with st.spinner("MATLAB Troubleshooter is thinking..."):
        # Get bot response
        bot_response = get_bot_response(user_input)
        
        # Add bot response to chat history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': bot_response,
            'timestamp': get_timestamp()
        })
    
    # Clear the input field and rerun to update the UI
    st.rerun()

def new_chat():
    """Reset chat to initial state"""
    st.session_state.chat_history = []
    st.session_state.conversation_started = False
    st.rerun()

def clear_chat_history():
    """Clear the chat history"""
    st.session_state.chat_history = []
    st.session_state.conversation_started = False
    st.rerun()

def change_theme(theme):
    """Change the app theme"""
    st.session_state.theme = theme
    # If user is logged in, update their preference
    if st.session_state.logged_in:
        st.session_state.user_data[st.session_state.username]["settings"]["theme"] = theme
        save_user_data(st.session_state.user_data)
    st.rerun()

def logout_user():
    """Log out the current user"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ------------- MAIN APP EXECUTION -------------
def main():
    """Main application entry point"""
    # Initialize the app
    initialize_app()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_navbar()
    
    # Display appropriate interface based on login status
    if not st.session_state.logged_in:
        render_auth_interface()
    else:
        render_chat_interface()

if __name__ == "__main__":
    main()