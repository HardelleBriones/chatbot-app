from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
)
from llama_index.core.node_parser import SentenceSplitter
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
from llama_index.core.query_engine import SubQuestionQueryEngine
import re
from typing import List
from dotenv import load_dotenv
load_dotenv()

embed_model = OpenAIEmbedding(model="text-embedding-3-small")
MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')

def add_data(course_name: str,data: List[Document],topic:str = ""):
    try:
        if not MONGO_URI:
            raise ValueError("MongoDB URI is required.")
        
        
        mongodb_client = pymongo.MongoClient(MONGO_URI)
        
        #Chunking
        # splitter = SemanticSplitterNodeParser(
        #     buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        #     )
        
        # nodes = splitter.get_nodes_from_documents(data)
        
        splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=20,
        )
        nodes = splitter.get_nodes_from_documents(data)
        #create a vector index
        store = MongoDBAtlasVectorSearch(mongodb_client,db_name="vector", collection_name=course_name)
        storage_context_vector = StorageContext.from_defaults(vector_store=store)
        VectorStoreIndex(nodes, storage_context=storage_context_vector, embed_model=embed_model)

        #add to docstore
        storage_context_docstore = StorageContext.from_defaults(
            docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=course_name, db_name="docstore"),
            )
        storage_context_docstore.docstore.add_documents(nodes)
    
        print("Successfully Added to the Knowledge base")
    except Exception as e:
        raise Exception("Error in adding data: "+str(e))

 