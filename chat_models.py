from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
