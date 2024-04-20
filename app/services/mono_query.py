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
from llama_index.core.tools import QueryEngineTool,ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
llm = OpenAI(temperature=0, model="gpt-3.5-turbo-0125")
MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
def add_data_mono(course_name: str,data: List[BaseNode]):
    try:
        mongodb_client = pymongo.MongoClient(MONGO_URI)
        store = MongoDBAtlasVectorSearch(mongodb_client,db_name="Course", collection_name=course_name)
        storage_context_vector = StorageContext.from_defaults(vector_store=store)
        #create a vector index
        VectorStoreIndex(
            data, storage_context=storage_context_vector, embed_model=embed_model
        )
        print(data)
        print("Successfully Added to the Knowledge base")
    except ValueError as e:
        print(f"An error occurred: {e}")
    
def create_vector_engine_atlas_mono(course_name):
    client = pymongo.MongoClient(MONGO_URI)
    vector_store = MongoDBAtlasVectorSearch(
        client,
        db_name="Course",
        collection_name=course_name,
        index_name=course_name
    )

    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine()
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
            system_prompt=f"""\
    You are a teacher agent designed to answer queries about topics on a class.
    You must use the tools provided when answering a question; .\
    """, )
    return agent

