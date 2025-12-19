"""
Medical Assistant - Streamlit Application
Professional doctor-recommendation chatbot for Islamabad and Lahore
"""

import streamlit as st
from typing import List, Dict
import os

# Import custom modules
from database import DoctorDatabase, init_database, import_csv_files, search_doctors
from gemini_agent import GeminiMedicalAgent
from config import (
    APP_NAME,
    MAX_DOCTORS_DISPLAY,
    THEME_COLORS,
    SUPPORTED_CITIES,
    DATABASE_PATH
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================================
# CUSTOM CSS STYLING - DARK THEME
# ============================================================================

def apply_custom_css():
    """Apply custom CSS for ChatGPT-like dark theme"""
    st.markdown("""
    <style>
        /* Main background - dark like ChatGPT */
        .stApp {
            background-color: #212121;
            color: #ececec;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Chat messages - ChatGPT style */
        [data-testid="stChatMessage"] {
            background-color: transparent !important;
            padding: 1.5rem 0 !important;
        }
        
        /* User message styling */
        [data-testid="stChatMessage"][data-testid*="user"] {
            background-color: #2f2f2f !important;
            border-radius: 12px;
            margin: 0.5rem 0;
        }
        
        /* Chat input - clean like ChatGPT */
        [data-testid="stChatInput"] {
            background-color: #2f2f2f !important;
            border: 1px solid #565656 !important;
            border-radius: 24px !important;
            padding: 0.5rem 1rem !important;
        }
        
        /* Ensure the input container itself is dark */
        [data-testid="stChatInput"] > div {
            background-color: #2f2f2f !important;
        }
        
        /* Make typed text visible - WHITE color and ensure background is dark */
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] input,
        .stChatInput textarea,
        .stChatInput input {
            background-color: #2f2f2f !important;
            color: #ffffff !important;
            border: none !important;
            font-size: 1rem !important;
            caret-color: #ffffff !important;
        }
        
        /* Placeholder text */
        [data-testid="stChatInput"] textarea::placeholder,
        .stChatInput textarea::placeholder {
            color: #888888 !important;
        }
        
        /* Fix the actual container block supplied by Streamlit */
        .stChatInputContainer {
            background-color: #212121 !important;
            padding: 1rem !important;
            border-top: none !important;
        }
        
        /* Style the send button */
        [data-testid="stChatInput"] button {
            background-color: #1e90ff !important;
            border-radius: 50% !important;
            color: white !important;
        }
        
        /* Chat message text */
        .stMarkdown {
            color: #ececec !important;
        }
        
        /* Side padding adjustment */
        .main .block-container {
            max-width: 800px;
            margin: 0 auto;
            padding-top: 1rem;
        }
        
        /* Avatar styling */
        [data-testid="stChatMessage"] [data-testid="stImage"] {
            border-radius: 50%;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #212121;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #424242;
            border-radius: 4px;
        }
        
        /* Links */
        a {
            color: #1e90ff !important;
        }
        
        /* Bold text */
        strong {
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_database():
    """Initialize database and import CSV files (cached)"""
    if not os.path.exists(DATABASE_PATH):
        with st.spinner("🏥 Initializing medical database..."):
            init_database()
            import_csv_files()
            st.success("✅ Database initialized successfully!")
    return True


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'agent' not in st.session_state:
        st.session_state.agent = GeminiMedicalAgent()
    
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = initialize_database()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def display_message(role: str, content: str):
    """Display a chat message with appropriate styling"""
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            {content}
        </div>
        """, unsafe_allow_html=True)


def process_user_query(user_message: str) -> str:
    """
    Process user query through Gemini AI (ChatGPT-style)
    Gemini decides when to use database
    """
    agent = st.session_state.agent
    
    # Check for emergency first
    if agent.detect_emergency(user_message):
        return agent.get_emergency_response()
    
    # Let Gemini handle EVERYTHING naturally
    # First, analyze if we need database
    intent_info = agent.classify_intent(user_message)
    
    # If it's a casual message or general query, let Gemini respond naturally
    if intent_info['intent_type'] == 'general_query':
        # Pure conversation - no database needed
        prompt = f"""User said: "{user_message}"

This is a casual message or general question. Respond naturally and helpfully like ChatGPT.

If they're greeting you, greet them back warmly.
If they're asking what you do, explain you help find doctors in Islamabad and Lahore.
If it's unclear, ask how you can help them find a doctor.

Be friendly, concise, and conversational."""
        
        try:
            response = agent.chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"[GEMINI ERROR] General query failed: {e}")
            return "Hi! I'm your Medical Assistant. I can help you find doctors in Islamabad and Lahore. What are you looking for today?"
    
    # If they mentioned unsupported city
    if intent_info['intent_type'] == 'unsupported_city':
        prompt = f"""User asked: "{user_message}"

They mentioned a city we don't support yet. We only have doctors in Islamabad and Lahore.

Politely explain this and ask if they'd like help finding a doctor in Islamabad or Lahore instead.
Be understanding and friendly."""
        
        try:
            response = agent.chat.send_message(prompt)
            return response.text
        except:
            return "I currently only have information about doctors in Islamabad and Lahore. Would you like me to help you find a doctor in one of these cities?"
    
    # They need a doctor - search database
    specialty = intent_info.get('specialty')
    city = intent_info.get('city')
    filters = intent_info.get('filters', {})
    
    search_params = {
        'specialty': specialty,
        'city': city,
        'limit': 5
    }
    
    if filters.get('gender'):
        search_params['gender_preference'] = filters['gender']
    if filters.get('budget_conscious'):
        search_params['max_fee'] = 3000
    
    # Get doctors from database
    doctors = search_doctors(**search_params)
    
    # Let Gemini create natural response with doctor info
    if doctors:
        # Build doctor info
        doctor_info = "\n\nDoctors from our database:\n"
        for i, doc in enumerate(doctors, 1):
            doctor_info += f"\n{i}. {doc['name']}"
            doctor_info += f"\n   - {doc['specialty']} in {doc['city']}"
            doctor_info += f"\n   - Specializations: {doc['specializations']}"
            doctor_info += f"\n   - Experience: {doc['experience']}"
            doctor_info += f"\n   - Reviews: {doc['reviews']}"
            doctor_info += f"\n   - Fee: Rs.{doc['fee']}"
            if doc['qualifications']:
                doctor_info += f"\n   - Qualifications: {doc['qualifications']}"
        
        prompt = f"""User asked: "{user_message}"

{doctor_info}

Respond naturally and conversationally like ChatGPT. Help them by:
- Acknowledging their request warmly
- Recommending 3-5 doctors from the list above
- Varying your style (don't always use the same format!)
- Highlighting key details: name, specialty, experience, reviews, fee
- Being helpful and friendly

IMPORTANT:
- Only mention doctors from the list above
- Vary how you present information each time
- Be conversational and natural
- If they ask follow-up questions, use conversation context"""
        
        try:
            response = agent.chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Error: {e}")
            # Simple fallback
            result = f"I found some great {specialty}s"
            if city:
                result += f" in {city}"
            result += f":\n\n"
            for i, doc in enumerate(doctors[:3], 1):
                result += f"{i}. **{doc['name']}** - {doc['experience']}, {doc['reviews']} reviews, Rs.{doc['fee']}\n"
            return result
    else:
        # No doctors found
        prompt = f"""User asked: "{user_message}"

We don't have any {specialty}s {"in " + city if city else ""} in our database yet.

Respond naturally and empathetically. Include:
1. Clear statement: "System will update in few days"
2. Apologize for not having what they need
3. Suggest trying a different specialty or city (Islamabad/Lahore)
4. Be conversational and brief"""
        
        try:
            response = agent.chat.send_message(prompt)
            return response.text
        except:
            return f"**System will update in few days.**\n\nI don't have {specialty}s {"in " + city if city else ""} in my database yet. Would you like to try a different specialty or city (Islamabad/Lahore)?"


# ============================================================================
# MAIN APPLICATION - ChatGPT Style
# ============================================================================

def main():
    """Main application function - ChatGPT Style"""
    
    # Apply custom styling
    apply_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Simple header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="color: #1e90ff; margin: 0;">🏥 Medical Assistant</h1>
        <p style="color: #888; margin: 0.5rem 0 0 0;">Find doctors in Islamabad & Lahore</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display chat messages (ChatGPT style)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input (ChatGPT style - fixed at bottom)
    if prompt := st.chat_input("Message Medical Assistant..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_user_query(prompt)
            st.markdown(response)
        
        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()

