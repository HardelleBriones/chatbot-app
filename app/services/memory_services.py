#mongodb://localhost:27017
from pymongo import MongoClient
import datetime
import uuid
from llama_index.core.llms import ChatMessage, MessageRole
# Replace with your MongoDB connection details
import os

class ChatHistory():
    def __init__(self):
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        client = MongoClient(MONGO_URI)
        db = client["chat_history"]
        self.conversations = db["conversations"]
    def add_message(self,user: str):
        try:
            # Check if conversation exists for the user
            conversation = self.conversations.find_one({"user_id": user})
            # Create new conversation if it doesn't exist
            if not conversation:
                conversation = {

                    "user_id": user,
                    "created_at": datetime.datetime.utcnow(),
                    "messages": [],
                }
                self.conversations.insert_one(conversation)

            # Create new message object
            new_message = {
                "message_id": str(uuid.uuid4()),
                "user_query": "who created one piece?",  # Assuming user is sending the message
                "bot": "I do not know",
                "user_reaction" : "Okiee",
                "timestamp": datetime.datetime.utcnow(),
            }
            self.conversations.update_one({"user_id": user}, {"$push": {"messages": new_message}})
            # # Add message to conversation
            # conversation["messages"].append(new_message)

            # # Save updated conversation with new message
            # conversations.save(conversation)
            

        except Exception as e:
            print(f"Error adding message: {e}")


    def get_chat_history(self,user: str):
        try:
            # User ID (replace with the actual user ID)

            # Find the conversation document for the user
            conversation = self.conversations.find_one({"user_id": user})

            if conversation:
                # Get all messages from the conversation
                messages = conversation["messages"]
                print(f"Messages for user {user}:")

                # Loop through each message and print its details (optional)
                chat_history = []
                for message in messages:
                    # print(f"\t- Message ID: {message['message_id']}")
                    # print(f"\t  User Query: {message['user_query']}")  # Assuming user sent the message
                    # print(f"\t  Bot Response: {message['bot']}")
                    # print(f"\t  Timestamp: {message['timestamp']}")
                    # print()  # Add a newline between messages
                    chat_history.append(ChatMessage(content=message['user_query'], role="user"))
                    chat_history.append(ChatMessage(content=message['bot'], role="assistant"))
                return chat_history
            else:
                print(f"No conversation found for user: {user}")

        except Exception as e:
            print(f"Error retrieving messages: {e}")



