from fastapi import APIRouter, Depends, HTTPException
from chat_models import ChatMessage, ChatResponse
import auth_utils
from chat_mongodb import get_chat_history, save_chat_message, manage_chat_limit
from chat_service import generate_chat_response

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.post("", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatMessage,
    current_user: dict = Depends(auth_utils.get_current_user_data)
):
    user_id = str(current_user["id"])
    role = current_user["role"] # 'student' or 'admin'
    user_message = request.message

    # 1. Retrieve last 10 messages for context
    history = await get_chat_history(user_id, limit=10)

    # 2. Add current message to history for LLM prompt
    # Note: 'history' already contains dicts with 'role' and 'message' (from MongoDB document structure)
    
    # 3. Generate response from Groq
    # Passing the current message and the history
    llm_response = await generate_chat_response(history + [{"role": "user", "message": user_message}], role)

    # 4. Save both user and assistant messages to MongoDB
    await save_chat_message(user_id, user_message, "user")
    await save_chat_message(user_id, llm_response, "assistant")

    # 5. Limit messages to last 10 (per prompt: "ensure that only the latest 10 interactions are stored")
    # Actually, the prompt says "the latest 10 messages" vs "the latest 10 interactions".
    # Usually "interactions" means pairs. Let's assume 10 messages (5 pairs) or 10 interactions (20 messages).
    # Re-reading: "storing the last 10 messages for each user". 10 messages total.
    await manage_chat_limit(user_id, limit=10)

    return {"response": llm_response}
