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
from typing import List
from dotenv import load_dotenv
load_dotenv()

embed_model = OpenAIEmbedding(model="text-embedding-3-small")
llm = OpenAI(temperature=0.7, model="gpt-3.5-turbo-0125")
MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')

def add_data_mono(course_name: str,data: List[Document],topic:str = ""):
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

    
def get_vector_index(course_name):
    try:
        client = pymongo.MongoClient(MONGO_URI)
        vector_store = MongoDBAtlasVectorSearch(
            client,
            db_name="vector",
            collection_name=course_name,
            index_name=course_name
        )
        index = VectorStoreIndex.from_vector_store(vector_store)
        return index
    except Exception as e:
        raise Exception("Error in getting vector index: " + str(e))

    # query_engine = index.as_query_engine()
    # return query_engine
def get_docstore(course_name):
    try:

        storage = StorageContext.from_defaults(
                docstore=MongoDocumentStore.from_uri(uri=MONGO_URI, namespace=course_name, db_name="docstore"),
                )
        return storage.docstore
    except Exception as e:
        raise Exception("Error in getting doc store: " + str(e))

def create_bm25_retriever(docstore):
    try: 
        bm25_retriever = BM25Retriever.from_defaults(
        docstore=docstore, similarity_top_k=2
        )
        return bm25_retriever
    except Exception as e:
        raise Exception("Error in creating bm25 retriever: " + str(e))

def query_fusion_retriever(vector_retriever, bm25_retriever):
    try:
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
    except Exception as e:
        raise Exception("Error in creating fusion retriever: " + str(e))

def create_query_engine_tool(vector_query_engine,name: str):
    # setup base query engine as tool
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name=name,
                description= f"Provides information about  {name} "
                    "Use a detailed plain text question as input to the tool."
            ),
        ),
    ]
    return query_engine_tools


def create_agent_mono(query_engine,course_name):
    try:
        query_engine_tool = QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name=course_name,
                description=(
                    f"Provides information about the {course_name} "
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
    except Exception as e:
        raise Exception("Error in creating agent: " + str(e))






