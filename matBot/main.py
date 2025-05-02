import streamlit as st
import time
import bcrypt
import json
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="MATLAB Troubleshooter",
    page_icon="🧮",
    layout="wide",
)

# Initialize database file for user accounts
USER_DB_PATH = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DB_PATH, 'w') as file:
        json.dump(data, file)

def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Initialize session state variables
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_user_data()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False

if 'theme' not in st.session_state:
    st.session_state.theme = "light"  # Default theme

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'username' not in st.session_state:
    st.session_state.username = ""

if 'auth_page' not in st.session_state:
    st.session_state.auth_page = "login"  # Options: login, signup

# Function to apply MATLAB-inspired theme with dark/light mode support
def apply_matlab_theme(theme_mode):
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
        
        .theme-selector {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 1rem 0;
            gap: 1rem;
        }
        
        .theme-btn {
            cursor: pointer;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            border: 2px solid var(--matlab-blue);
            transition: all 0.2s ease;
        }
        
        .theme-btn.active {
            background-color: var(--matlab-blue);
            color: white;
            font-weight: bold;
        }
        
        .theme-btn:not(.active) {
            background-color: transparent;
            color: var(--matlab-blue);
        }
        
        .theme-btn:hover:not(.active) {
            background-color: rgba(0,118,168,0.1);
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
        
        /* Toggle switch styling */
        .theme-toggle {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .theme-toggle-label {
            margin-right: 0.5rem;
            color: #E0E0E0;
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

# Function to get current timestamp
def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

# Function to simulate bot response (replace with actual RAG implementation)
def get_bot_response(user_input):
    # This is a placeholder for your actual RAG implementation
    time.sleep(1)  # Simulate processing time
    
    if "plot" in user_input.lower():
        return """To create a plot in MATLAB, you can use the `plot(x,y)` function. Here's an example:

```matlab
x = 0:0.1:2*pi;
y = sin(x);
plot(x, y)
title('Sine Wave')
xlabel('x')
ylabel('sin(x)')
grid on
```

You can customize your plot with various options:
- Change line style with `plot(x, y, '--')` for dashed lines
- Change color with `plot(x, y, 'r')` for red
- Add multiple plots with `hold on` followed by additional plot commands"""

    elif "error" in user_input.lower() or "issue" in user_input.lower():
        return """When troubleshooting MATLAB errors, follow these professional practices:

1. **Verify variable types** using `class(variable_name)`
2. **Check array dimensions** with `size(array_name)` or `whos`
3. **Implement error handling** with `try/catch` blocks:
```matlab
try
    % Code that might cause an error
    result = riskyOperation();
catch ME
    % Handle the error
    fprintf('Error: %s\\n', ME.message);
    % Alternative actions
end
```
4. **Debug efficiently** by setting breakpoints:
   - Use `dbstop if error` to pause at error locations
   - Or `dbstop in function_name at line_number` for specific breakpoints
   
5. **Check MATLAB path issues** with `path` or fix with `addpath()`"""

    elif "function" in user_input.lower():
        return """MATLAB functions are defined in .m files with this structure:

```matlab
function [output1, output2] = myFunction(input1, input2)
    % Function description (will show in help)
    % 
    % Inputs:
    %   input1 - Description of first input
    %   input2 - Description of second input
    %
    % Outputs:
    %   output1 - Description of first output
    %   output2 - Description of second output
    
    % Function implementation
    output1 = input1 + input2;
    output2 = input1 * input2;
end
```

Best practices for MATLAB functions:
- Place each function in its own .m file named exactly like the function
- Use meaningful variable names
- Include comprehensive help documentation
- Validate input arguments at the start of your function
- Use `nargin` to handle optional arguments"""

    elif "matrix" in user_input.lower():
        return """Matrices are fundamental in MATLAB. Here's a comprehensive guide:

**Creating matrices:**
```matlab
% Direct specification
A = [1, 2, 3; 4, 5, 6; 7, 8, 9]

% Special matrices
zeros_mat = zeros(3,4)     % 3x4 matrix of zeros
ones_mat = ones(2,5)       % 2x5 matrix of ones
eye_mat = eye(4)           % 4x4 identity matrix
rand_mat = rand(3,3)       % 3x3 random matrix (uniform dist.)
randn_mat = randn(3,3)     % 3x3 random matrix (normal dist.)
diag_mat = diag([1,2,3])   % Diagonal matrix
magic_square = magic(3)    % Magic square matrix
```

**Matrix operations:**
```matlab
transpose_A = A'           % Transpose
inverse_A = inv(A)         % Matrix inverse (if invertible)
det_A = det(A)             % Determinant
eigenvalues = eig(A)       % Eigenvalues
[V,D] = eig(A)             % Eigenvalues and eigenvectors
trace_A = trace(A)         % Trace (sum of diagonal elements)
rank_A = rank(A)           % Matrix rank
null_A = null(A)           % Null space
```

**Matrix manipulation:**
```matlab
size_A = size(A)           % Matrix dimensions
[rows, cols] = size(A)     % Get dimensions separately
submatrix = A(1:2, 2:3)    % Extract submatrix
A(2,:) = [10,11,12]        % Replace a row
A(:,3) = [13;14;15]        % Replace a column
flipped = flip(A)          % Flip array vertically
rotated = rot90(A)         % Rotate array 90 degrees
```"""

    elif "simulink" in user_input.lower():
        return """Simulink is MATLAB's block diagram environment for multi-domain simulation. Here are the basics:

1. **Start Simulink**:
   ```matlab
   simulink
   ```

2. **Create a new model**:
   - Click "Blank Model" or use `new_system('model_name')`
   - Save with `save_system('model_name')`

3. **Add blocks from libraries**:
   - Use the Library Browser or search functionality
   - Common blocks: Integrator, Transfer Fcn, Gain, Scope, etc.

4. **Connect blocks** by clicking and dragging from output to input ports

5. **Set parameters** by double-clicking blocks

6. **Run simulation**:
   - Set simulation parameters in the "Modeling" tab
   - Click "Run" or use `sim('model_name')`

7. **Analyze results** using Scope blocks or by exporting to MATLAB workspace

For debugging Simulink models:
- Enable signal logging
- Use breakpoints
- Check sample times
- Verify solver settings"""

    else:
        return """I'm your MATLAB troubleshooting assistant. I can help with:

- Syntax and function usage
- Debugging errors and warnings
- Algorithm implementation
- Best practices and optimization
- Simulink modeling
- Data visualization techniques
- File I/O and data processing

Could you provide more specific details about your MATLAB question or issue?"""

# Function to handle example queries
def handle_example_query(query):
    st.session_state.chat_history.append({
        'role': 'user',
        'content': query,
        'timestamp': get_timestamp()
    })
    
    bot_response = get_bot_response(query)
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': bot_response,
        'timestamp': get_timestamp()
    })
    
    st.rerun()

# Apply the selected theme
apply_matlab_theme(st.session_state.theme)

# Create sidebar with settings
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/21/Matlab_Logo.png", width=120)
    st.header("MATLAB Troubleshooter")
    st.markdown("---")
    
    st.subheader("Theme Settings")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌙 Dark", key="dark_theme", 
                    help="Switch to dark theme", 
                    use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()
    with col2:
        if st.button("☀️ Light", key="light_theme", 
                    help="Switch to light theme", 
                    use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()
    
    st.markdown("---")
    st.subheader("Chat Options")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.conversation_started = False
        st.rerun()
    
    st.markdown("---")
    st.subheader("📚 Helpful Resources")
    
    st.markdown("""
    <div class="resource-card">
        <div class="resource-title">📖 Documentation</div>
        <a href="https://www.mathworks.com/help/matlab/" target="_blank">MATLAB Documentation</a>
    </div>
    
    <div class="resource-card">
        <div class="resource-title">💬 Community</div>
        <a href="https://www.mathworks.com/matlabcentral/answers/" target="_blank">MATLAB Answers</a>
    </div>
    
    <div class="resource-card">
        <div class="resource-title">🎓 Tutorials</div>
        <a href="https://www.mathworks.com/support/learn-with-matlab-tutorials.html" target="_blank">MATLAB Tutorials</a>
    </div>
    
    <div class="resource-card">
        <div class="resource-title">🔍 Function Search</div>
        <a href="https://www.mathworks.com/help/search.html" target="_blank">Search Functions</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("© 2025 MATLAB Troubleshooter v1.0")

# Main chat interface
st.markdown("""
<div class="logo-container">
    <h1>MATLAB Troubleshooter</h1>
    <p>Your professional assistant for MATLAB problem-solving</p>
</div>
""", unsafe_allow_html=True)

# Example queries section
st.markdown("### Quick Examples")
cols = st.columns(3)
with cols[0]:
    st.markdown("""
    <div class="example-card" onclick="document.getElementById('user_input').value='How do I plot data in MATLAB?'; document.getElementById('submit_button').click();">
        How do I plot data in MATLAB?
    </div>
    """, unsafe_allow_html=True)
with cols[1]:
    st.markdown("""
    <div class="example-card" onclick="document.getElementById('user_input').value='Help with matrix operations'; document.getElementById('submit_button').click();">
        Help with matrix operations
    </div>
    """, unsafe_allow_html=True)
with cols[2]:
    st.markdown("""
    <div class="example-card" onclick="document.getElementById('user_input').value='How to debug errors in MATLAB?'; document.getElementById('submit_button').click();">
        How to debug errors in MATLAB?
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Display chat history
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

# File uploader for MATLAB files
st.markdown("### Upload MATLAB File (Optional)")
uploaded_file = st.file_uploader("Upload .m or .mat files for specific help", type=["m", "mat"])
if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully! Ask a question about it.")

# User input area with improved styling
st.markdown("### Ask Your Question")
user_input = st.text_input("Type your MATLAB question here:", key="user_input", placeholder="E.g., How do I solve linear equations in MATLAB?")

col1, col2, col3 = st.columns([6, 1, 1])

with col1:
    pass

with col2:
    submit_button = st.button("Submit", key="submit_button", use_container_width=True)
    # Add JavaScript to allow pressing Enter to submit
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && document.activeElement.id === 'user_input') {
            document.getElementById('submit_button').click();
        }
    });
    </script>
    """, unsafe_allow_html=True)

with col3:
    if st.button("Clear", key="clear_button", use_container_width=True):
        st.session_state.user_input = ""
        st.rerun()

# Handle submit button
if submit_button:
    if user_input.strip():
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

# Add a professional footer
st.markdown("""
<div class="footer">
    <p>MATLAB Troubleshooter - Powered by advanced RAG technology</p>
    <p>Designed to help you solve MATLAB problems efficiently and effectively</p>
</div>
""", unsafe_allow_html=True)