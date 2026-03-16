import os
from groq import AsyncGroq
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

# Ensure the client is initialized only if the key exists
if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
    client = AsyncGroq(api_key=GROQ_API_KEY)
else:
    client = None

STUDENT_BASE_PROMPT = """
You are a helpful university assistant for Campus-AI.
Your goal is to assist students with course information, assignments, policies, and guidance.

# FORMATTING RULES:
1. Always answer in exactly 3 numbered points.
2. Start each point on a new line.
3. Include a very short intro (Max 1 line).
"""

STUDENT_ENG_EXAMPLE = """
# EXAMPLE (English):
User: Tell me about the library.
Bot: Here is some information about our campus library:
1. The library is open from 8:00 AM to 8:00 PM.
2. You can borrow up to 5 books at a time.
3. A valid student ID card is required for entry.
"""

STUDENT_HIN_EXAMPLE = """
# EXAMPLE (Hinglish):
User: library kab khulti hai?
Bot: Library ki timings aur rules ye hain:
1. Library subah 8 baje se raat 8 baje tak khuli rehti hai.
2. Aap ek baar mein 5 books borrow kar sakte hain.
3. Entry ke liye aapke paas student ID card hona zaroori hai.
"""

ADMIN_BASE_PROMPT = """
You are a faculty/admin assistant for Campus-AI.
Your goal is to assist teachers and admins with procedures, policies, records, and guidelines.

# FORMATTING RULES:
1. Always answer in exactly 3 numbered points.
2. Start each point on a new line.
3. Include a very short intro (Max 1 line).
"""

ADMIN_ENG_EXAMPLE = """
# EXAMPLE (English):
User: How to update attendance?
Bot: To update student attendance, follow these steps:
1. Log in to the faculty portal and select your course.
2. Navigate to the attendance section for the current date.
3. Mark students and click the submit button.
"""

ADMIN_HIN_EXAMPLE = """
# EXAMPLE (Hinglish):
User: attendance update kaise karein?
Bot: Attendance update karne ka tareeka ye hai:
1. Faculty portal par log in karein aur apna course select karein.
2. Aaj ki date ke liye attendance section mein jayein.
3. Students ko mark karke submit button par click karein.
"""

def detect_lingo(text: str) -> str:
    """
    Heuristic to detect if a message is Hinglish based on common particles.
    """
    hindi_particles = [
        "hai", "hoon", "hain", "karo", "kyu", "kya", "kaise", "batao", "dikhao", 
        "dekhna", "hoga", "ko", "se", "bhi", "liye", 
        "kuch", "sakte", "chahiye", "kab", "kahaan", "kaun"
    ]
    text_lower = str(text).lower()
    # Check for whole words to avoid partial matches
    import re
    words = re.findall(r'\b\w+\b', text_lower)
    for p in hindi_particles:
        if p in words:
            return "Hinglish"
    return "English"

def get_system_prompt(role: str, lingo: str, user_name: str) -> str:
    base = ADMIN_BASE_PROMPT if role == "admin" else STUDENT_BASE_PROMPT
    
    # Inject user's identity to establish long-term memory context
    base += f"\n\n[CRITICAL CONTEXT] The user's name is {user_name}. You MUST remember this. If they ask if you remember them or their name, affirm enthusiastically that you do remember them as {user_name}!"
    
    if lingo == "Hinglish":
        return base + "\n\n" + (ADMIN_HIN_EXAMPLE if role == "admin" else STUDENT_HIN_EXAMPLE)
    return base + "\n\n" + (ADMIN_ENG_EXAMPLE if role == "admin" else STUDENT_ENG_EXAMPLE)

async def generate_chat_response(messages: list, role: str, user_name: str = "User") -> str:
    if not client:
        return "Chatbot Error: GROQ_API_KEY is missing or invalid in .env."

    # 1. Detect language of the latest user input
    last_user_msg = ""
    for msg in messages[::-1]:
        if msg.get("role") == "user":
            last_user_msg = msg.get("message") or msg.get("content", "")
            break
    
    lingo = detect_lingo(last_user_msg)
    
    # 2. Augment system prompt with the detected language requirement & user name
    system_prompt = get_system_prompt(role, lingo, user_name)
    system_prompt += f"\n\nCRITICAL ACTION: The user's requested language is {lingo}.\nRESPONSE REQUIREMENT: You MUST answer ENTIRELY in {lingo}. NEVER mix languages."
    
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
            temperature=0.1, # Lowest temperature for extreme consistency
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
