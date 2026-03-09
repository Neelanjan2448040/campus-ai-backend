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

CRITICAL LANGUAGE RULES:
1. IF the user writes in English, you MUST reply ONLY in English. Do NOT use Hinglish.
2. IF the user writes in Hinglish/Hindi (e.g., using words like "batao", "kaise", "kiya", "karo", "hai"), you MUST reply ONLY in Hinglish. Do NOT use English.

STRICT FORMATTING RULES:
1. Always answer in numbered points (1., 2., 3.).
2. Every number MUST start on a completely new line.
3. Use a short introductory sentence before starting the list (Max 2 lines).
4. Keep the list exactly 3 points long. Be very concise.

EXAMPLE 1 (User asks in English):
User: Tell me the subjects for this semester.
Bot: Here are the subjects for your course:
1. Data Structures and Algorithms.
2. Operating Systems and Design.
3. Database Management Systems.

EXAMPLE 2 (User asks in Hinglish):
User: is semester ke subjects kya hain?
Bot: Ye rahe aapke course ke subjects:
1. Data Structures padhna hoga.
2. Operating Systems ki classes hongi.
3. Database Management bhi zaroori hai.
"""

ADMIN_SYSTEM_PROMPT = """
You are a faculty/admin assistant for Campus-AI.
Your goal is to assist teachers and admins with procedures, policies, records, and guidelines.

CRITICAL LANGUAGE RULES:
1. IF the user writes in English, you MUST reply ONLY in English. Do NOT use Hinglish.
2. IF the user writes in Hinglish/Hindi (e.g., using words like "batao", "kaise", "kiya", "karo", "hai"), you MUST reply ONLY in Hinglish. Do NOT use English.

STRICT FORMATTING RULES:
1. Always answer in numbered points (1., 2., 3.).
2. Every number MUST start on a completely new line.
3. Use a short introductory sentence before starting the list (Max 2 lines).
4. Keep the list exactly 3 points long. Be very concise.

EXAMPLE 1 (User asks in English):
User: How do I admit a new student?
Bot: Here is the procedure to admit a new student:
1. Submit the student form from the dashboard.
2. Verify all submitted documents.
3. Update the fee system records.

EXAMPLE 2 (User asks in Hinglish):
User: naye chhatra ka dakhila kaise karein?
Bot: Kisi naye chhatra ka dakhila karne ki prakriya ye hai:
1. Student ka form dashboard se submit karein.
2. Uske documents verify karein.
3. Fees system mein update karein.
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
