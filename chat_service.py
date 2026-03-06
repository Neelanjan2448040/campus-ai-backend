import os
from groq import AsyncGroq
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"

# Ensure the client is initialized only if the key exists
if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
    client = AsyncGroq(api_key=GROQ_API_KEY)
else:
    client = None

STUDENT_SYSTEM_PROMPT = """
You are a helpful university assistant for Campus-AI. Your primary goal is to assist students with their academic and campus-related needs.
You should behave as a helpful university assistant and answer questions related to:
- course information
- assignments
- campus rules and policies
- general academic guidance
- fee related queries

If the student introduces their name (e.g., "My name is Rahul"), you MUST remember it and use it when they ask "What is my name?".
Keep your responses concise, professional, and appropriate for a college environment.
If you do not have specific data available, recommend that the student contacts the university administration.
"""

ADMIN_SYSTEM_PROMPT = """
You are a faculty assistant for Campus-AI. Your role is to assist teachers and administrators with faculty-related inquiries.
You should behave as a faculty assistant and answer questions related to:
- teacher salary structure
- leave policies and paid leaves
- faculty responsibilities
- administrative guidelines

Keep your responses concise, professional, and appropriate for a college environment.
"""

def get_system_prompt(role: str) -> str:
    if role == "admin":
        return ADMIN_SYSTEM_PROMPT
    return STUDENT_SYSTEM_PROMPT

async def generate_chat_response(messages: list, role: str) -> str:
    if not client:
        return "Chatbot Error: GROQ_API_KEY is missing or invalid in .env."

    system_prompt = get_system_prompt(role)
    llm_messages = [{"role": "system", "content": system_prompt}]
    
    # Filter and format messages properly for Groq
    for msg in messages:
        content = msg.get("message") or msg.get("content")
        role_name = msg.get("role")
        if content and role_name:
            llm_messages.append({
                "role": role_name,
                "content": str(content)
            })
    
    try:
        completion = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=llm_messages,
            temperature=0.7,
            max_tokens=512, # Sufficient for college assistant
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API Error: {str(e)}")
        if "401" in str(e) or "api_key" in str(e).lower():
            return "Chatbot Error: Your Groq API Key is invalid or unauthorized."
        return f"I'm sorry, I'm having trouble connecting to my brain right now. Please try again."
