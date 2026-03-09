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
You are a helpful university assistant for Campus-AI.
Your goal is to assist students with course information, assignments, policies, and guidance.

STRICT FORMATTING RULES:
1. Always answer in numbered points (1., 2., 3.).
2. Every number MUST start on a completely new line.
3. Use a short introductory sentence before starting the list.
4. Separate the intro from the list with a blank line.
5. Do NOT use literal '\\n' text; use actual line breaks.

EXAMPLE OF CORRECT FORMAT:
Here are the subjects for your course:

1. Data Structures and Algorithms.
2. Operating Systems and Design.
3. Database Management Systems.
"""

ADMIN_SYSTEM_PROMPT = """
You are a faculty assistant for Campus-AI.
Your goal is to assist teachers with salary structures, leaves, policies, and guidelines.

STRICT FORMATTING RULES:
1. Always answer in numbered points (1., 2., 3.).
2. Every number MUST start on a completely new line.
3. Use a short introductory sentence before starting the list.
4. Separate the intro from the list with a blank line.
5. Do NOT use literal '\\n' text; use actual line breaks.

EXAMPLE OF CORRECT FORMAT:
Here are the leave policy details:

1. Faculty are entitled to 12 paid leaves.
2. Sabbatical requests require 6 months notice.
3. Sick leave requires a medical certificate.
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
            temperature=0.3, # Even lower temperature for strict adherence to formatting
            max_tokens=600,
        )
        llm_text = completion.choices[0].message.content
        
        # AGGRESSIVE CLEANUP:
        # 1. Standardize literal "\n" into real newlines
        clean_text = llm_text.replace("\\n", "\n").replace("\\", "").strip()
        
        # 2. Force every sequence like " 2. " or " 3. " onto a new line if the AI didn't do it
        import re
        # Look for digit followed by period when it follows a space but is not at the start of a line
        clean_text = re.sub(r' +(\d+)\.', r'\n\1.', clean_text)
        
        # 3. Collapse multiple newlines into a standard double newline for better spacing
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)
        
        return clean_text.strip()
    except Exception as e:
        logger.error(f"Groq API Error: {str(e)}")
        if "401" in str(e) or "api_key" in str(e).lower():
            return "Chatbot Error: Your Groq API Key is invalid or unauthorized."
        return f"I'm sorry, I'm having trouble connecting to my brain right now. Please try again."
