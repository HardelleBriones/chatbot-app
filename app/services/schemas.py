from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class Message(BaseModel):
    message_id: str 
    user_query:str
    ai_response: str
    user_reaction: Optional[int] = 0
    timestamp: datetime = datetime.utcnow()

class Conversation(BaseModel):
    user_id: str
    created_at: datetime = datetime.utcnow()
    subject: str
    messages: List[Message] = []


class Text_knowledgeBase(BaseModel):
    topic: str
    text: str


