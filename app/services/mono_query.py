
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
)

from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.core import Document
import os
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import Document
import pymongo
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.tools import QueryEngineTool,ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SemanticSplitterNodeParser
from typing import List
from dotenv import load_dotenv
load_dotenv()

embed_model = OpenAIEmbedding(model="text-embedding-3-small")
llm = OpenAI(temperature=0.7, model="gpt-3.5-turbo-0125")
MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')

def add_data_mono(course_name: str,data: List[Document],topic:str = ""):
    try:
        mongodb_client = pymongo.MongoClient(MONGO_URI)
        
        for doc in data:
            doc.metadata["Topic"] = topic
            doc.excluded_embed_metadata_keys  = ["file_path","file_size","creation_date","last_modified_date"]

        #Chunking
        splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
            )
        nodes = splitter.get_nodes_from_documents(data)


        #create a vector index
        store = MongoDBAtlasVectorSearch(mongodb_client,db_name="Course", collection_name=course_name)
        storage_context_vector = StorageContext.from_defaults(vector_store=store)
        VectorStoreIndex(nodes, storage_context=storage_context_vector, embed_model=embed_model)

        #add to docstore
        storage_context_docstore = StorageContext.from_defaults(
            docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=course_name, db_name="Course_docstore"),
            )
        storage_context_docstore.docstore.add_documents(nodes)
    
        print("Successfully Added to the Knowledge base")
    except ValueError as e:
        print(f"An error occurred: {e}")

    
def get_vector_index(course_name):
    client = pymongo.MongoClient(MONGO_URI)
    vector_store = MongoDBAtlasVectorSearch(
        client,
        db_name="Course",
        collection_name=course_name,
        index_name=course_name
    )

    index = VectorStoreIndex.from_vector_store(vector_store)
    return index

    # query_engine = index.as_query_engine()
    # return query_engine
def get_docstore(course_name):
    storage = StorageContext.from_defaults(
            docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=course_name, db_name="Course_docstore"),
            )
    return storage.docstore

def create_bm25_retriever(docstore):
    bm25_retriever = BM25Retriever.from_defaults(
    docstore=docstore, similarity_top_k=2
    )
    return bm25_retriever

def query_fusion_retriever(vector_retriever, bm25_retriever):
    retriever = QueryFusionRetriever(
    [vector_retriever, bm25_retriever],
    similarity_top_k=2,
    num_queries=1,  # set this to 1 to disable query generation
    mode="reciprocal_rerank",
    use_async=True,
    verbose=True,
    # query_gen_prompt="...",  # we could override the query generation prompt here
    )
    query_engine = RetrieverQueryEngine.from_args(retriever)
    return query_engine


def create_agent_mono(query_engine,course_name):
    query_engine_tool = QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name=f"Class_{course_name}",
            description=(
                f"Provides information about the different topics of class {course_name} "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
    agent = OpenAIAgent.from_tools(
            query_engine_tool,
            llm=llm,
            verbose=True,
            
            system_prompt = f"""\
    You are an agent designed to answer queries about {course_name} class.
    Your primary goal is to provide clear and concise explanations, offer helpful resources or examples when necessary, 
    Use the context and your own extensive knowledge to craft responses that are personalized and comprehensive, ensuring that students receive the most insightful answers possible
    If the query is not related to the class then respond by saying \"I am desigen to answer queries about {course_name}\"
    The exception is if their is a context provided by the Class_{course_name} then you can use the context to answer the question.
    
"""

, 
)
    return agent




def delete_file(course_name: str, file_name_to_delete: str):
    client = pymongo.MongoClient(MONGO_URI)
    db = client["Course_docstore"] 


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

    db = client["Course"] 
    collection = db[course_name]
    filter_criteria_ref_doc_info = {"metadata.file_name": file_name_to_delete}
    result = collection.delete_many(filter_criteria_ref_doc_info)
    print("Deleted node vector:", result.deleted_count)


# def delete_file_vectorstore(course_name: str, file_name_to_delete: str):
#     client = pymongo.MongoClient(MONGO_URI)
#     db = client["vector_subject2"] 
#     collection = db[course_name]
#     filter_criteria_ref_doc_info = {"metadata.file_name": file_name_to_delete}
#     result = collection.delete_many(filter_criteria_ref_doc_info)
#     print("Deleted node vector:", result.deleted_count)



def add_file_to_course(course_name, file_name):
    client = pymongo.MongoClient(MONGO_URI)
    db = client["Course"] 
    course_collection = db["records"]
    # Check if the course already exists
    course = course_collection.find_one({'course_name': course_name})
    if course:
        # Course already exists, check if file name exists in the list
        if file_name in course['file_names']:
            print(f"File '{file_name}' already exists for course '{course_name}'.")
            return True
        else:
            # Add file name to the existing course
            course_collection.update_one(
                {'_id': course['_id']},
                {'$push': {'file_names': file_name}}
            )
            print(f"File '{file_name}' added to course '{course_name}'.")
            return False
    else:
        # Course doesn't exist, create a new document
        course_collection.insert_one({'course_name': course_name, 'file_names': [file_name]})
        print(f"Course '{course_name}' created with file '{file_name}'.")
        return False

def get_all_files(course_name:str):
    client = pymongo.MongoClient(MONGO_URI)
    db = client["Course"] 
    course_collection = db["records"]
    # Query the collection based on the course name
    result = course_collection.find_one({"course_name": course_name})
    # Check if the course exists
    if result:
        # Extract and return the list of file names
        file_names = result.get("file_names", [])
        if file_names:
            return file_names
        else:
            return None
    else:
        raise ValueError("Course not found")

def get_all_course():
    client = pymongo.MongoClient(MONGO_URI)

    # Check if the "records" collection exists
    if "Course" not in client.list_database_names():
        raise ValueError("Records collection does not exist")
    
    db = client["Course"] 
    # Check if the "records" collection exists
    if "records" not in db.list_collection_names():
        raise ValueError("Records collection does not exist")
    
    course_collection = db["records"]
    result = course_collection.find({})
    course_names = [doc["course_name"] for doc in result]
    return course_names


def delete_course_file(course_name: str, file_name:str):
    client = pymongo.MongoClient(MONGO_URI)
    # Check if the "records" collection exists
    if "Course" not in client.list_database_names():
        raise ValueError("Records collection does not exist")
    
    db = client["Course"] 

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
    else:
        raise ValueError("Course not found")
    