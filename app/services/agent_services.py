from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    SummaryIndex,
    StorageContext,
)
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.core.llms import ChatMessage
from typing import List
from llama_index.core import load_index_from_storage
from llama_index.agent.openai_legacy import FnRetrieverOpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from llama_index.core.objects import ObjectIndex, SimpleToolNodeMapping
import os
from llama_index.vector_stores.chroma import ChromaVectorStore
import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import Settings
Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
db = chromadb.PersistentClient(path="../chroma_db")
MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")

def create_vector_engine(collection):
    #add exception if collection is not found
    collection_name = db.get_collection(collection)  
    vector_store = ChromaVectorStore(chroma_collection=collection_name)
    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    vector_query_engine = vector_index.as_query_engine()
    print("Successfully created vector engine")
    # print(vector_query_engine.query("What do you know?"))
    return vector_query_engine
def create_vector_engine_atlas(collection_name,db_name):
    client = pymongo.MongoClient(MONGO_URI)
    vector_store = MongoDBAtlasVectorSearch(
        client,
        db_name=f"vector_{db_name}",
        collection_name=collection_name,
        index_name=collection_name
    )

    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine()
    # print("-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(query_engine.query("what do you know?"))
    # print("-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    return query_engine


def create_summary_engine(collection):
    storage_context = StorageContext.from_defaults(
docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=collection, db_name="docstore"),
index_store=MongoIndexStore.from_uri(uri=MONGO_URI, namespace=collection, db_name="index"),
)
    summary_index = load_index_from_storage(storage_context)
    summary_query_engine = summary_index.as_query_engine()
    return summary_query_engine
def create_summary_engine_atlas(collection,db_name):
    storage_context = StorageContext.from_defaults(
docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=collection, db_name=f"docstore_{db_name}"),
index_store=MongoIndexStore.from_uri(uri=MONGO_URI, namespace=collection, db_name=f"index_{db_name}"),
)
    summary_index = load_index_from_storage(storage_context)
    summary_query_engine = summary_index.as_query_engine()
    return summary_query_engine

def create_engine_tools(vector_query_engine,summary_query_engine, collection):

    # define tools
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="vector_tool",
                description=(
                    "Useful for questions related to specific aspects of"
                    f" {collection}"
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=summary_query_engine,
            metadata=ToolMetadata(
                name="summary_tool",
                description=(
                    "Useful for any requests that require a holistic summary"
                f" of EVERYTHING about {collection}. For questions about"
                " more specific sections, please use the vector_tool."
                ),
            ),
        ),
    ]
    return query_engine_tools
def create_document_agent(query_engine_tools,collection):
    agents = {}
            # build agent
    function_llm = OpenAI(model="gpt-4")
    agent = OpenAIAgent.from_tools(
        query_engine_tools,
        llm=function_llm,
        verbose=True,
        system_prompt=f"""\
You are a specialized agent designed to answer queries about {collection}.
You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge.\
""",
    )

    #agents[collection] = agent
    return agent
def convert_tool_agent(collection_names,agents):
    #number of agents must be the same as collection names
    # define tool for each document agent
    all_tools = []
    for collection in collection_names:
        summary = (
            f"This content contains articles about {collection}. Use"
            f" this tool if you want to answer any questions about {collection}.\n"
        )
        doc_tool = QueryEngineTool(
            query_engine=agents[collection],
            metadata=ToolMetadata(
                name=f"tool_{collection}",
                description=summary,
            ),
        )
        all_tools.append(doc_tool)
    return all_tools
def create_object_index(all_tools):
    tool_mapping = SimpleToolNodeMapping.from_objects(all_tools)
    obj_index = ObjectIndex.from_objects(
        all_tools,
        tool_mapping,
        VectorStoreIndex,
    )
    return obj_index
def fnRetriever(obj_index):
    top_agent = FnRetrieverOpenAIAgent.from_retriever(
    obj_index.as_retriever(similarity_top_k=3),
    system_prompt=""" \
You are an agent designed to answer queries about anime.
Please always use the tools provided to answer a question. Do not rely on prior knowledge.

\

""",
    
    verbose=True,
    
)
    #response = top_agent.query("What is Bleach?")
    return top_agent





