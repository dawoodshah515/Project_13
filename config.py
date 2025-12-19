"""
Configuration file for Medical Assistant Chatbot
Contains API keys, database settings, and medical domain mappings
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key():
    """Retrieve API key from environment or streamlit secrets"""
    # 1. Try environment variable (Local .env)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
        
    # 2. Try Streamlit Secrets (Cloud)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        pass
    except Exception:
        pass
        
    # 3. Fallback (Direct Key - For easiest deployment)
    return "AIzaSyC0kjy25NW1SeydAXhUErRmxe8a1l-n1VY"

# ============================================================================
# API CONFIGURATION
# ============================================================================
GEMINI_API_KEY = get_api_key()
GEMINI_MODEL = "models/gemini-2.5-flash"  # Latest flash model

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_PATH = "doctors.db"
CSV_DIRECTORY = "."  # Current directory where CSV files are located

# ============================================================================
# SUPPORTED LOCATIONS
# ============================================================================
SUPPORTED_CITIES = ["Islamabad", "Lahore"]

# ============================================================================
# SYMPTOM TO SPECIALTY MAPPING
# ============================================================================
SYMPTOM_SPECIALTY_MAP = {
    "Psychiatrist": [
        "anxiety", "depression", "panic", "insomnia", "mental health", "stress",
        "bipolar", "ocd", "obsessive", "compulsive", "ptsd", "trauma", "suicide",
        "suicidal", "self harm", "mood swings", "schizophrenia", "psychosis",
        "hallucination", "delusion", "sleep disorder", "eating disorder",
        "anorexia", "bulimia", "adhd", "attention deficit", "anger management"
    ],
    "Dermatologist": [
        "rash", "acne", "eczema", "skin", "itching", "psoriasis", "allergic reaction",
        "hives", "dermatitis", "pigmentation", "melasma", "vitiligo", "warts",
        "moles", "skin tag", "fungal infection", "ringworm", "hair loss",
        "alopecia", "dandruff", "scalp", "nail", "pimples", "blackheads",
        "wrinkles", "aging skin", "dry skin", "oily skin", "sunburn"
    ],
    "Neurologist": [
        "headache", "migraine", "seizure", "numbness", "tingling", "paralysis",
        "stroke", "epilepsy", "tremor", "parkinsons", "multiple sclerosis",
        "neuropathy", "vertigo", "dizziness", "memory loss", "dementia",
        "alzheimers", "confusion", "weakness", "facial pain", "trigeminal",
        "bells palsy", "sciatica", "nerve pain", "coordination problems"
    ],
    "Gynecologist": [
        "pregnancy", "menstrual", "period", "pcos", "infertility", "pelvic pain",
        "ovarian", "uterine", "vaginal", "cervical", "breast", "menopause",
        "contraception", "miscarriage", "abortion", "prenatal", "postnatal",
        "labor", "delivery", "cesarean", "fibroids", "endometriosis",
        "irregular periods", "painful periods", "heavy bleeding", "discharge"
    ],
    "Urologist": [
        "urinary", "kidney", "bladder", "prostate", "uti", "stones", "incontinence",
        "frequent urination", "painful urination", "blood in urine", "hematuria",
        "erectile dysfunction", "impotence", "kidney stone", "bladder infection",
        "prostate enlargement", "bph", "urethral", "testicular", "scrotal",
        "male infertility", "penis", "urology"
    ]
}

# ============================================================================
# EMERGENCY KEYWORDS
# ============================================================================
EMERGENCY_KEYWORDS = [
    # Cardiac emergencies
    "chest pain", "heart attack", "cardiac arrest", "heart failure",
    
    # Mental health emergencies
    "suicidal", "suicide", "kill myself", "end my life", "self harm",
    "want to die", "better off dead",
    
    # Bleeding
    "severe bleeding", "heavy bleeding", "bleeding profusely", "hemorrhage",
    
    # Respiratory
    "difficulty breathing", "cant breathe", "choking", "suffocating",
    "shortness of breath", "gasping",
    
    # Neurological
    "stroke", "face drooping", "slurred speech", "sudden weakness",
    "sudden numbness", "severe headache", "worst headache",
    
    # Allergic
    "severe allergic reaction", "anaphylaxis", "throat closing", "swelling throat",
    
    # Consciousness
    "loss of consciousness", "passed out", "unconscious", "unresponsive",
    
    # Trauma
    "severe injury", "major accident", "broken bone", "head injury"
]

# ============================================================================
# UI THEME COLORS (Dark Theme with Bluish Highlights)
# ============================================================================
THEME_COLORS = {
    "background": "#0a0a0a",
    "primary": "#1e90ff",
    "secondary": "#4169e1",
    "accent": "#00bfff",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "card_bg": "#1a1a1a",
    "border": "#2a2a2a",
    "success": "#00ff88",
    "warning": "#ffaa00",
    "error": "#ff4444"
}

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
APP_NAME = "Medical Assistant"
MAX_DOCTORS_DISPLAY = 5
MAX_CONVERSATION_HISTORY = 10

# ============================================================================
# NO DATA MESSAGE
# ============================================================================
NO_DATA_MESSAGE = "System will update in few days."
