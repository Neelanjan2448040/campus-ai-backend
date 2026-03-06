import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "campus_ai_chat")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[MONGODB_DB]
chat_collection = db["conversations"]

async def get_chat_history(user_id: str, limit: int = 10):
    """
    Retrieve the last 'limit' messages for a user.
    Messages are returned in chronological order.
    """
    cursor = chat_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    history = await cursor.to_list(length=limit)
    # Reverse to get chronological order (oldest first for LLM)
    return history[::-1]

async def save_chat_message(user_id: str, message: str, role: str):
    """
    Save a message (either from 'user' or 'assistant') to MongoDB.
    """
    document = {
        "user_id": user_id,
        "message": message,
        "role": role,
        "timestamp": datetime.utcnow()
    }
    await chat_collection.insert_one(document)

async def manage_chat_limit(user_id: str, limit: int = 10):
    """
    Ensure only the last 'limit' messages are stored for a user.
    """
    count = await chat_collection.count_documents({"user_id": user_id})
    if count > limit:
        # Find the oldest messages that exceed the limit
        to_delete = count - limit
        oldest_docs = await chat_collection.find({"user_id": user_id}).sort("timestamp", 1).limit(to_delete).to_list(length=to_delete)
        ids_to_delete = [doc["_id"] for doc in oldest_docs]
        await chat_collection.delete_many({"_id": {"$in": ids_to_delete}})
