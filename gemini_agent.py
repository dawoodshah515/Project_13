"""
Gemini AI Agent for Medical Assistant Chatbot
Handles symptom analysis, intent classification, and response generation
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import re

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SYMPTOM_SPECIALTY_MAP,
    EMERGENCY_KEYWORDS,
    SUPPORTED_CITIES,
    NO_DATA_MESSAGE
)


class GeminiMedicalAgent:
    """AI agent for medical query processing and response generation"""
    
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        
        # System instruction for conversational medical assistant
        system_instruction = """You are a friendly and professional Medical Assistant chatbot.
        
        Your role is to help users find suitable doctors in Islamabad and Lahore, Pakistan.
        
        IMPORTANT RULES:
        1. Be conversational, warm, and natural - like a helpful friend
        2. ONLY recommend doctors from the database provided in each query
        3. NEVER invent or guess doctor information
        4. Vary your responses - don't use the same format every time
        5. Be concise but informative
        6. Adapt your tone to the user's query
        7. Remember conversation context
        
        When recommending doctors:
        - Introduce them naturally in conversation
        - Include key details (name, fee, experience, reviews) but vary the format
        - Explain WHY you're recommending them
        - Be helpful about next steps
        
        If no doctors found:
        - Say "System will update in few days" clearly
        - Be understanding and offer alternatives
        
        For emergencies:
        - Immediately advise seeking emergency help
        - Provide emergency numbers
        """
        
        self.model = genai.GenerativeModel(
            GEMINI_MODEL,
            system_instruction=system_instruction
        )
        self.chat = None
        self.reset_conversation()
    
    def detect_emergency(self, user_message: str) -> bool:
        """
        Detect emergency situations from user message
        Returns True if emergency keywords detected
        """
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in EMERGENCY_KEYWORDS)
    
    def get_emergency_response(self) -> str:
        """Generate emergency response message"""
        return """🚨 **MEDICAL EMERGENCY DETECTED** 🚨

**PLEASE SEEK IMMEDIATE MEDICAL ATTENTION:**

• Call emergency services (Rescue 1122)
• Go to the nearest emergency room
• Contact your nearest hospital immediately

**For Islamabad:**
- PIMS Hospital Emergency: 051-9261170
- Shifa International Hospital: 051-8463100

**For Lahore:**
- Jinnah Hospital Emergency: 042-99231536
- Shaukat Khanum Hospital: 042-35905000

Your life and safety are the top priority. Please seek professional medical help immediately before considering any doctor consultations.
"""
    
    def extract_city_from_query(self, user_message: str) -> Optional[str]:
        """
        Extract city name from user query
        Returns 'Islamabad', 'Lahore', or None
        """
        message_lower = user_message.lower()
        
        if 'islamabad' in message_lower or 'isb' in message_lower or 'isl' in message_lower:
            return 'Islamabad'
        elif 'lahore' in message_lower or 'lhr' in message_lower:
            return 'Lahore'
        
        return None
    
    def map_symptoms_to_specialty(self, user_message: str) -> Optional[str]:
        """
        Map user symptoms to medical specialty
        Uses keyword matching from SYMPTOM_SPECIALTY_MAP
        """
        message_lower = user_message.lower()
        
        # Count matches for each specialty
        specialty_scores = {}
        
        for specialty, keywords in SYMPTOM_SPECIALTY_MAP.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    score += 1
            if score > 0:
                specialty_scores[specialty] = score
        
        # Return specialty with highest score
        if specialty_scores:
            return max(specialty_scores, key=specialty_scores.get)
        
        return None
    
    def classify_intent(self, user_message: str) -> Dict:
        """
        Classify user intent and extract information
        
        Returns dict with:
        - intent_type: 'doctor_search', 'symptom_search', 'general_query', 'unsupported_city'
        - specialty: extracted or mapped specialty
        - city: extracted city
        - filters: additional filters (gender, area, budget)
        """
        result = {
            'intent_type': 'general_query',
            'specialty': None,
            'city': None,
            'filters': {}
        }
        
        message_lower = user_message.lower()
        
        # Extract city
        result['city'] = self.extract_city_from_query(user_message)
        
        # Check for unsupported cities
        unsupported_cities = ['karachi', 'peshawar', 'quetta', 'multan', 'faisalabad', 'rawalpindi']
        if any(city in message_lower for city in unsupported_cities):
            result['intent_type'] = 'unsupported_city'
            return result
        
        # Check for direct specialty mention
        for specialty in SYMPTOM_SPECIALTY_MAP.keys():
            if specialty.lower() in message_lower:
                result['specialty'] = specialty
                result['intent_type'] = 'doctor_search'
                break
        
        # If no direct specialty, check for symptom-based search
        if not result['specialty']:
            mapped_specialty = self.map_symptoms_to_specialty(user_message)
            if mapped_specialty:
                result['specialty'] = mapped_specialty
                result['intent_type'] = 'symptom_search'
        
        # Extract filters
        # Gender preference
        if 'female' in message_lower or 'lady' in message_lower or 'woman' in message_lower:
            result['filters']['gender'] = 'female'
        elif 'male' in message_lower or 'man doctor' in message_lower:
            result['filters']['gender'] = 'male'
        
        # Budget/Fee preference
        if 'cheap' in message_lower or 'affordable' in message_lower or 'low fee' in message_lower:
            result['filters']['budget_conscious'] = True
        
        return result
    
    def reset_conversation(self):
        """Reset the chat session"""
        self.chat = self.model.start_chat(history=[])
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        # Gemini chat automatically maintains history
        pass
    
    def generate_response(
        self, 
        user_message: str, 
        retrieved_doctors: List[Dict],
        intent_info: Dict
    ) -> str:
        """
        Generate conversational chatbot response using Gemini AI
        STRICT RULE: Only use data from retrieved_doctors, no hallucination
        """
        
        # Handle no data scenario
        if not retrieved_doctors:
            return self._generate_no_data_response_conversational(intent_info)
        
        # Build context for the AI
        doctor_context = "\n\nAvailable doctors matching your request:\n"
        
        for i, doctor in enumerate(retrieved_doctors, 1):
            doctor_context += f"\n{i}. **{doctor['name']}**"
            doctor_context += f"\n   - {doctor['specialty']} in {doctor['city']}"
            doctor_context += f"\n   - Specializations: {doctor['specializations']}"
            if doctor['qualifications']:
                doctor_context += f"\n   - Qualifications: {doctor['qualifications']}"
            doctor_context += f"\n   - Experience: {doctor['experience']}"
            doctor_context += f"\n   - Reviews: {doctor['reviews']}"
            doctor_context += f"\n   - Fee: Rs.{doctor['fee']}"
        
        # Create a natural prompt
        prompt = f"""User asked: \"{user_message}\"

{doctor_context}

Please respond naturally and conversationally. Help the user by:
1. Briefly acknowledging their request
2. Recommending 3-5 of the best doctors from the list above (vary your presentation style)
3. Highlighting why each doctor is a good fit
4. Being friendly and helpful

IMPORTANT: 
- Only use information from the doctors listed above
- Never invent information
- Vary your response style - don't be repetitive
- Be conversational and natural
- Include key details: name, specialty, fee, experience, reviews
- If contact/timings/hospital info is missing, you can mention "Contact details available at clinic" instead of "Not provided"""
        
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            # DEBUG: Show error on UI for Cloud debugging
            import streamlit as st
            st.error(f"⚠️ Gemini Cloud Error: {str(e)}")
            print(f"Error generating AI response: {e}")
            return self._generate_fallback_response(retrieved_doctors, intent_info)
    
    def _generate_no_data_response_conversational(self, intent_info: Dict) -> str:
        """Generate conversational response when no doctors found"""
        specialty = intent_info.get('specialty', 'that specialty')
        city = intent_info.get('city', 'the city you mentioned')
        
        # Use Gemini to generate a natural no-data response
        prompt = f"""The user is looking for a {specialty} in {city}, but we don't have any doctors in our database for this request.

Generate a friendly, empathetic response that:
1. Clearly states: \"{NO_DATA_MESSAGE}\"
2. Apologizes for not having what they need
3. Explains we're expanding our database
4. Offers helpful alternatives (search different specialty, try Islamabad or Lahore, describe symptoms)
5. Keep it conversational and brief (2-3 sentences plus alternatives)

Be natural and vary your wording each time."""
        
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except:
            # Fallback
            response = f"I apologize, but I couldn't find any {specialty}s"
            if city:
                response += f" in {city}"
            response += f" in our current database.\n\n**{NO_DATA_MESSAGE}**\n\n"
            response += "We're continuously adding more doctors. Would you like to try a different specialty or city (Islamabad/Lahore)?"
            return response
    
    def _generate_fallback_response(self, doctors: List[Dict], intent_info: Dict) -> str:
        """Generate formatted response without AI (fallback)"""
        specialty = intent_info.get('specialty', 'doctors')
        city = intent_info.get('city', '')
        
        response = f"Based on your request, here are the top recommended {specialty}s"
        if city:
            response += f" in {city}"
        response += ":\n\n"
        
        for i, doctor in enumerate(doctors[:5], 1):
            response += f"**Doctor #{i}: {doctor['name']}**\n"
            response += f"- **Specialty:** {doctor['specialty']}\n"
            response += f"- **City / Area:** {doctor['city']}\n"
            response += f"- **Specializations:** {doctor['specializations']}\n"
            response += f"- **Qualifications:** {doctor['qualifications']}\n"
            response += f"- **Experience:** {doctor['experience']}\n"
            response += f"- **Reviews:** {doctor['reviews']}\n"
            response += f"- **Fee:** Rs.{doctor['fee']}\n"
            response += f"- **Clinic / Hospital:** Not provided\n"
            response += f"- **Contact:** Not provided\n"
            response += f"- **Timings:** Not provided\n"
            response += f"- **Profile Link:** Not provided\n\n"
        
        return response
    
    def get_clarification_response(self) -> str:
        """Generate response asking for clarification"""
        return """I'd be happy to help you find the right doctor! To provide the best recommendations, could you please:

1. **Specify your medical concern or symptoms**, OR
2. **Tell me which type of specialist you need** (e.g., Psychiatrist, Dermatologist, Neurologist, Gynecologist, Urologist)
3. **Mention your preferred city** (Islamabad or Lahore)

**Examples:**
- "I need a psychiatrist in Lahore for anxiety"
- "Best dermatologist in Islamabad"
- "I have severe headaches and dizziness"

How can I assist you today?"""
    
    def get_unsupported_city_response(self) -> str:
        """Generate response for unsupported cities"""
        return """I apologize, but our database currently only covers doctors in **Islamabad** and **Lahore**.

We are working on expanding our coverage to other cities across Pakistan.

Would you like me to recommend doctors in:
1. **Islamabad**
2. **Lahore**

Please let me know your medical concern and preferred city from the above options!"""


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_agent() -> GeminiMedicalAgent:
    """Create and return a new Gemini Medical Agent instance"""
    return GeminiMedicalAgent()


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    print("Testing Gemini Medical Agent")
    print("=" * 60)
    
    agent = GeminiMedicalAgent()
    
    # Test cases
    test_queries = [
        "I need a psychiatrist in Lahore",
        "Anxiety and panic attacks",
        "Best dermatologist in Islamabad",
        "I'm having chest pain",
        "Doctor in Karachi",
        "Female gynecologist near me"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        # Check emergency
        if agent.detect_emergency(query):
            print("⚠️ EMERGENCY DETECTED")
        
        # Classify intent
        intent = agent.classify_intent(query)
        print(f"Intent Type: {intent['intent_type']}")
        print(f"Specialty: {intent['specialty']}")
        print(f"City: {intent['city']}")
        print(f"Filters: {intent['filters']}")
