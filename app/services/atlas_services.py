import chromadb
from llama_index.core import (
    VectorStoreIndex,
    SummaryIndex,
    StorageContext,
)
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Document
from llama_index.core.schema import BaseNode
from typing import List
import os
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
import re
import pymongo
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
def add_data_atlas(collection: str,db_name: str,data: List[BaseNode]):
    try:
        MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
        mongodb_client = pymongo.MongoClient(MONGO_URI)
        store = MongoDBAtlasVectorSearch(mongodb_client,db_name=f"vector_{db_name}", collection_name=collection)
        storage_context_vector = StorageContext.from_defaults(vector_store=store)
        #create a vector index
        VectorStoreIndex(
            data, storage_context=storage_context_vector
        )
        storage_context = StorageContext.from_defaults(
        docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=collection, db_name=f"docstore_{db_name}"),
        index_store=MongoIndexStore.from_uri(uri=MONGO_URI, namespace=collection, db_name=f"index_{db_name}"),
        )
        #create a summary index
        SummaryIndex(data, storage_context=storage_context)
        print("Successfully Added to the Knowledge base")
    except ValueError as e:
        print(f"An error occurred: {e}")


def format_collection_name(name):
    # Remove leading and trailing whitespaces
    name = name.strip()

    # Replace spaces with underscores
    name = name.replace(' ', '_')

    # Remove non-alphanumeric characters, underscores, and hyphens
    name = re.sub(r'[^\w-]', '', name)
    # Ensure the name does not exceed 63 characters
    name = name[:63]

    return name



def get_vector_databases():
    # Connect to MongoDB
    mongodb_client = pymongo.MongoClient(MONGO_URI)

    # Get list of all database names
    db_names = mongodb_client.list_database_names()

    # Filter out databases that start with "vector"
    vector_databases = [name.replace("vector_", "",1) for name in db_names if name.startswith("vector_")]

    return vector_databases

def check_database_exists(db_name):
    mongodb_client = pymongo.MongoClient(MONGO_URI)
    # Check if the specified database exists
    format_db = "vector_"+db_name
    database_exists = format_db in mongodb_client.list_database_names()

    return database_exists


#get all collection from db

def get_collections(db_name):
    mongodb_client = pymongo.MongoClient(MONGO_URI)
    format_db = "vector_"+db_name
    # Access the specified database
    db = mongodb_client[format_db]
    # Get list of all collection names
    collection_names = db.list_collection_names()

    return collection_names

# def check_collection_index(db_name,collection_name):
#     mongodb_client = pymongo.MongoClient(MONGO_URI)
#     format_db = "vector_"+db_name
#     # Access the specified database
#     db = mongodb_client[format_db]
#     # Get list of all collection names
#     collection = db[collection_name]
#     indexes = collection.list_indexes()
#     print(collection_name)
#     print(str(indexes)+"/*/*/*/*/*/*/*/*")
#     print(bool(indexes))
#     print("*/*/*/*/*/*/*/*/*/*/*/*")
#     return bool(indexes)

