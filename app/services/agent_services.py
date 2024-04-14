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

class ItemManager:
    def __init__(self):
        self.db = chromadb.PersistentClient(path="../chroma_db")
        self.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
        #embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
        self.node_parser = SentenceSplitter()
        self.MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
    def create_vector_engine(self,collection):
        #add exception if collection is not found
        collection_name = self.db.get_collection(collection)  
        vector_store = ChromaVectorStore(chroma_collection=collection_name)
        vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        vector_query_engine = vector_index.as_query_engine()
        print("Successfully created vector engine")
        # print(vector_query_engine.query("What do you know?"))
        return vector_query_engine
    def create_summary_engine(self,collection):
        storage_context = StorageContext.from_defaults(
    docstore=MongoDocumentStore.from_uri(uri=self.MONGO_URI, namespace=collection, db_name="docstore"),
    index_store=MongoIndexStore.from_uri(uri=self.MONGO_URI, namespace=collection, db_name="index"),
)
        summary_index = load_index_from_storage(storage_context)
        summary_query_engine = summary_index.as_query_engine()
        return summary_query_engine
    def create_engine_tools(self,vector_query_engine,summary_query_engine, collection):

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
    def create_document_agent(self,query_engine_tools,collection):
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
    def convert_tool_agent(self,collection_names,agents):
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
    def create_object_index(self,all_tools):
        tool_mapping = SimpleToolNodeMapping.from_objects(all_tools)
        obj_index = ObjectIndex.from_objects(
            all_tools,
            tool_mapping,
            VectorStoreIndex,
        )
        return obj_index
    def fnRetriever(self,obj_index):
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
    




