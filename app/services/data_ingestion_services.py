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
from dotenv import load_dotenv
load_dotenv()
chroma_client = chromadb.PersistentClient(path="../chroma_db")
def add_data(filename: str,data: List[BaseNode]):
    try:
        MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
        chroma_collection = chroma_client.create_collection(filename)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context_vector = StorageContext.from_defaults(vector_store=vector_store)
        #create a vector index
        VectorStoreIndex(data, storage_context=storage_context_vector)
        storage_context = StorageContext.from_defaults(
        docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=filename, db_name="docstore"),
        index_store=MongoIndexStore.from_uri(uri=MONGO_URI, namespace=filename, db_name="index"),
        )
        #create a summary index
        SummaryIndex(data, storage_context=storage_context)
        print("Successfully Added to the Knowledge base")
    except ValueError as e:
        print(f"An error occurred: {e}")

import re

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




