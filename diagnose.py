import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

async def test_connections():
    print("--- Diagnostic Tool ---")
    
    # 1. Test MongoDB
    try:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
        client = AsyncIOMotorClient(mongo_url)
        await client.admin.command('ping')
        print("[SUCCESS] MongoDB is reachable.")
    except Exception as e:
        print(f"[FAILED] MongoDB Connection Error: {e}")

    # 2. Test Groq
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or "your_groq" in api_key:
            print("[FAILED] Groq API Key is either missing or still a placeholder.")
        else:
            g_client = AsyncGroq(api_key=api_key)
            response = await g_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            print("[SUCCESS] Groq API is responding.")
    except Exception as e:
        print(f"[FAILED] Groq API Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connections())
