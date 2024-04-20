from fastapi import Depends, status, HTTPException, Response, APIRouter
from services.agent_services import (create_vector_engine,
                                     create_summary_engine,
                                     create_engine_tools,
                                     create_document_agent,
                                     convert_tool_agent,
                                     create_object_index,
                                     fnRetriever,
                                     create_vector_engine_atlas,
                                     create_summary_engine_atlas)
from services.atlas_services import get_collections
from services.memory_services import ChatHistory

import chromadb
router = APIRouter(
    prefix="/query",
    tags=["query"]
)    
chroma_client = chromadb.PersistentClient(path="../chroma_db")
#add db_name for the course
@router.get("/")
def query(query: str):
    try:
        agents = {}
        names = chroma_client.list_collections()
        collections = [collection.name for collection in names]
        for collection in collections:
            #also add db to specify the collection
            vector = create_vector_engine(collection)
            summary = create_summary_engine(collection)
            tools = create_engine_tools(vector,summary,collection)
            agent = create_document_agent(tools,collection)
            agents[collection] = agent
        all_tools = convert_tool_agent(collections,agents)
        obj_index = create_object_index(all_tools)
        #chat_history1 =  get_chat_history("user")
        top_agent = fnRetriever(obj_index)
        #chat_history = chat_history1
        response = top_agent.chat(query)
        return str(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

#add db_name for the course
@router.get("/atlas")
def query_atlas(query: str, subject:str, user: str ="user"):

    try:
        
        agents = {}
        
        collections = get_collections(subject)
        print(collections)
        if not collections:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subject found")
        
        for collection in collections:
            #also add db to specify the collection
            vector = create_vector_engine_atlas(collection,subject)
            summary = create_summary_engine_atlas(collection,subject)
            tools = create_engine_tools(vector,summary,collection)
            agent = create_document_agent(tools,collection)
            agents[collection] = agent
        all_tools = convert_tool_agent(collections,agents)
        obj_index = create_object_index(all_tools)
        #chat_history1 =  get_chat_history("user")
        user_conversation = ChatHistory(subject=subject,user_id=user)
        top_agent = fnRetriever(obj_index)
        #chat_history = chat_history1
        response = top_agent.chat(query, user_conversation.get_chat_history())
        user_conversation.add_message(query,str(response))
        return str(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")