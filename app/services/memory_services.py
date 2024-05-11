#mongodb://localhost:27017
from pymongo import MongoClient
import datetime
import uuid
from llama_index.core.llms import ChatMessage, MessageRole
from data_definitions.schemas import Message, Conversation
import os
from dotenv import load_dotenv
load_dotenv()
class ChatHistory():
    def __init__(self, subject:str, user_id:str ="user"):
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        client = MongoClient(MONGO_URI)
        db = client["chat_history"]
        self.conversations = db[subject]
        self.user_id = user_id
        self.subject = subject
    def add_message(self,user_query:str, ai_response:str):
        try:
            # Check if conversation exists for the user
            conversation = self.conversations.find_one({"user_id": self.user_id})
            # Create new conversation if it doesn't exist
            if not conversation:
                new_conversation_data = Conversation(user_id=self.user_id, subject=self.subject)
                self.conversations.insert_one(new_conversation_data.model_dump())

            # Create new message object
            new_message_data = Message(message_id=str(uuid.uuid4()),user_query=user_query, ai_response=ai_response)
            self.conversations.update_one({"user_id": self.user_id}, {"$push": {"messages": new_message_data.model_dump()}})
        except Exception as e:
            print(f"Error adding message: {e}")


    def get_chat_history(self):
        try:
            # Find the conversation document for the user
            conversation = self.conversations.find_one({"user_id": self.user_id})

            if conversation:
                # Get all messages from the conversation
                messages = conversation["messages"]
   
                # Limit the messages to the first 10 items
                messages = messages[::-1][:10]
                messages.reverse()
                chat_history = []
                for message in messages:
                    print(message['user_query'])
                    chat_history.append(ChatMessage(content=message['user_query'], role="user"))
                    chat_history.append(ChatMessage(content=message['ai_response'], role="assistant"))
                return chat_history
            else:
                print(f"No conversation found for user: {self.user_id}")
        except Exception as e:
            print(f"Error retrieving messages: {e}")



