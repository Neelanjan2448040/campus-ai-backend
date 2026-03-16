from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from chat_models import ChatMessage, ChatResponse
import auth_utils
from chat_mongodb import get_chat_history, save_chat_message, manage_chat_limit
from chat_service import generate_chat_response

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.get("/history")
async def get_history(current_user: dict = Depends(auth_utils.get_current_user_data)):
    user_id = str(current_user["id"])
    history = await get_chat_history(user_id, limit=30)
    output = []
    
    # We must ensure the history order is preserved (oldest first or newest first)
    # The frontend expects older messages first to append properly, but the UI logic in Chatbot.jsx appends it.
    for msg in history:
        output.append({
            "id": str(msg["_id"]),
            "role": "bot" if msg["role"] == "assistant" else "user",
            "text": msg["message"],
            "time": msg["timestamp"].strftime("%I:%M %p")
        })
    return {"history": output}

@router.post("", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatMessage,
    current_user: dict = Depends(auth_utils.get_current_user_data),
    db: Session = Depends(get_db)
):
    user_id = str(current_user["id"])
    role = current_user["role"] # 'student' or 'admin'
    user_message = request.message

    # Get user name for personalized long-term memory integration
    if role == "admin":
        user_info = db.query(models.Admin).filter(models.Admin.id == int(user_id)).first()
    else:
        user_info = db.query(models.Student).filter(models.Student.id == int(user_id)).first()
    
    user_name = user_info.name if user_info and hasattr(user_info, 'name') else "User"

    # 1. Retrieve last 10 messages for context (Short term memory)
    history = await get_chat_history(user_id, limit=20)

    # 2. Add current message to history for LLM prompt
    # Note: 'history' already contains dicts with 'role' and 'message' (from MongoDB document structure)
    
    # 3. Generate response from Groq
    # Passing the current message and the history
    llm_response = await generate_chat_response(history + [{"role": "user", "message": user_message}], role, user_name)

    # 4. Save both user and assistant messages to MongoDB
    await save_chat_message(user_id, user_message, "user")
    await save_chat_message(user_id, llm_response, "assistant")

    # 5. Limit messages to last 30 for optimization
    await manage_chat_limit(user_id, limit=30)

    return {"response": llm_response}
