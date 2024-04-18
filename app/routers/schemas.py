from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class Message(BaseModel):
    """
    Container for a single user record.
    """
    message_id: Optional[str] = None
    user_query: str
    bot: str
    user_reaction: Optional[str] = None  # Optional field for user reaction
    timestamp: datetime = datetime.utcnow()
class CollectionChange(BaseModel):
    old_collection: str
    new_collection: str

class Query(BaseModel):
    user_query:str
    ai_response: str

class Message(Query):
    message_id: str 
    user_reaction: Optional[str] = 0
    timestamp: datetime 

class Conversation(BaseModel):
    user_id: str
    created_at: datetime = datetime.utcnow()
    messages: List[Message] = []

class User(BaseModel):
    """
    Container for a single user record.
    """

    name: str
    school_id: str
    email: EmailStr
    department: str
    account_type: str 
    created_at: datetime = None
class UserCreate(User):
    """
    Schema for creating a new user.
    """
    password: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr

class Course(BaseModel):
    displayname: str
    urls: List[str]