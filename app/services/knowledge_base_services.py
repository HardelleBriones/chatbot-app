import os
import pymongo
import re
from typing import List
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
def delete_file(course_name: str, file_name_to_delete: str):
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client["docstore"] 


        collection_data = db[f"{course_name}/data"]
        filter_criteria_data = {"__data__.metadata.file_name": file_name_to_delete}
        # Delete documents matching the filter criteria
        result = collection_data.delete_many(filter_criteria_data)
        # Print the number of deleted documents
        print("Deleted count data:", result.deleted_count)

        filter_criteria_ref_doc_info = {"metadata.file_name": file_name_to_delete}
        
        collection_ref_doc_info = db[f"{course_name}/ref_doc_info"]
        documents_to_delete = collection_ref_doc_info.find(filter_criteria_ref_doc_info)
        # Extract _id values from the documents
        ids_to_delete = [doc["_id"] for doc in documents_to_delete]
        result = collection_ref_doc_info.delete_many(filter_criteria_ref_doc_info)
        print("Deleted count ref_doc_info:", result.deleted_count)

        deleted_count = 0
        collection_metadata = db[f"{course_name}/metadata"]
        for doc_id in ids_to_delete:
            result = collection_metadata.delete_many({"ref_doc_id": doc_id})
            deleted_count += result.deleted_count
        print("Deleted count metadata:",deleted_count)

        db_vector = client["vector"] 
        collection = db_vector[course_name]
        filter_criteria_ref_doc_info = {"metadata.file_name": file_name_to_delete}
        result = collection.delete_many(filter_criteria_ref_doc_info)
        print("Deleted node vector:", result.deleted_count)

        if collection_data.count_documents({}) == 0:
            # If it's empty, delete the collection
            db.drop_collection(f"{course_name}/data")

        if collection_ref_doc_info.count_documents({}) == 0:
            # If it's empty, delete the collection
            db.drop_collection(f"{course_name}/ref_doc_info")
            
        if collection_metadata.count_documents({}) == 0:
            # If it's empty, delete the collection
            db.drop_collection(f"{course_name}/metadata")
        if collection.count_documents({}) == 0:
            # If it's empty, delete the collection
            db_vector.drop_collection(course_name)
        

    except Exception as e:
        raise Exception("Error in deleting file: " + str(e))

def add_file_to_course(course_name, file_name):
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client["vector"] 
        course_collection = db["records"]
        # Check if the course already exists
        course = course_collection.find_one({'course_name': course_name})
        if course:
            # Add file name to the existing course
            course_collection.update_one(
                {'_id': course['_id']},
                {'$push': {'file_names': file_name}}
            )
            print(f"File '{file_name}' added to course '{course_name}'.")
        else:
            # Course doesn't exist, create a new document
            course_collection.insert_one({'course_name': course_name, 'file_names': [file_name]})
            print(f"Course '{course_name}' created with file '{file_name}'.")
    except Exception as e:
        raise Exception("Error in adding file in records: " + str(e))

def get_all_files(course_name:str):
    try:

        client = pymongo.MongoClient(MONGO_URI)
        db = client["vector"] 
        course_collection = db["records"]
        # Query the collection based on the course name
        result = course_collection.find_one({"course_name": course_name})
        # Check if the course exists
        if result:
            # Extract and return the list of file names
            file_names = result.get("file_names", [])
            
            if file_names:
                return file_names
        return []

    except Exception as e:
        raise Exception("Error in getting all files in records: ", str(e))


def get_all_course():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        # Check if the "records" collection exists
        if "vector" not in client.list_database_names():
            raise ValueError("Records collection does not exist")
        
        db = client["vector"] 
        # Check if the "records" collection exists
        if "records" not in db.list_collection_names():
            raise ValueError("Records collection does not exist")
        
        course_collection = db["records"]
        result = course_collection.find({})
        course_names = [doc["course_name"] for doc in result]
        return course_names
    except Exception as e:
        raise Exception("Error in getting all course: " + str(e))


def delete_course_file(course_name: str, file_name:str):
    try: 
        client = pymongo.MongoClient(MONGO_URI)
        # Check if the "records" collection exists
        if "vector" not in client.list_database_names():
            raise ValueError("Records collection does not exist")
        
        db = client["vector"] 

        # Check if the "records" collection exists
        if "records" not in db.list_collection_names():
            raise ValueError("Records collection does not exist")
        
        course_collection = db["records"]
        # Check if the course exists
        course = course_collection.find_one({'course_name': course_name})
        if course:
            course_collection.update_one(
                        {'_id': course['_id']},
                        {'$pull': {'file_names': file_name}}
                    )
            # Retrieve the updated course document
            updated_course = course_collection.find_one({'_id': course['_id']})
             # If the file list becomes empty, delete the entire document
            if 'file_names' in updated_course and not updated_course['file_names']:
                course_collection.delete_one({'_id': course['_id']})
                print(f"Document for course '{course_name}' deleted because file list became empty.")
        else:
            raise ValueError("Course not found")
    except Exception as e:
        raise Exception("Error in deleting course file: " +str(e))
        

def valid_index_name(name:str):
  """Checks if a string contains only valid characters (letters, numbers, hyphens, or underscores).

  Args:
      s: The string to be checked.

  Returns:
      True if the string contains only valid characters, False otherwise.
  """

  # Improved pattern for clarity and potential whitespace handling
  pattern = r"^[a-zA-Z0-9_-]+$"

  # Match the pattern at the beginning and end of the string for completeness
  return bool(re.match(pattern, name))
