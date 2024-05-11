from pymongo import MongoClient
from datetime import datetime
from data_definitions.schemas import UserCreate, UserUpdate
from dotenv import load_dotenv
load_dotenv()
import os
# Replace with your MongoDB connection string
connection_string = os.getenv('MONGODB_CONNECTION_STRING')

# Connect to MongoDB
client = MongoClient(connection_string)

# Get the database and collection
db = client["chatbot"]
collection = db["users"]


def create_user(user: UserCreate):
  """
  Creates a new user in the database.

  Args:
      user: User data to create.
  """
  existing_user = collection.find_one({"school_id": user.school_id})
  if existing_user:
    return {"error": "School ID already exists"}
  
  user_data = user.dict()
  user_data["created_at"] = datetime.utcnow()  # Set the current timestamp
  
  collection.insert_one(user_data)
  return user_data


def get_all_users():
  """
  Retrieves all users from the database.
  """
  users = list(collection.find())
  if users:
    print("Users:")
    return users
  else:
    return None


def get_user_by_school_id(school_id: str):
  """
  Retrieves a user by school ID from the database.

  Args:
      school_id: User's school identifier to search for.
  """
  user = collection.find_one({"school_id": school_id})
  if user:
    return user
  else:
    return None

def update_user(school_id: str, new_data: UserUpdate):
  """
  Updates an existing user's data in the database based on school ID.

  Args:
      school_id: User's school identifier to update.
      new_data: Dictionary containing new user data to update.
  """
  result = collection.update_one(
      {"school_id": school_id}, {"$set": new_data}
  )
  return result.matched_count



def delete_user(school_id: str):
  """
  Deletes a user from the database based on school ID.

  Args:
      school_id: User's school identifier to delete.
  """
  result = collection.delete_one({"school_id": school_id})
  return result.deleted_count 
