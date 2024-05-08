from fastapi import Depends, status, HTTPException, Response, APIRouter
from services.mono_query import create_query_engine_tool, get_vector_index, get_all_course
from services.atlas_services import get_collections
from services.memory_services import ChatHistory
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core import get_response_synthesizer
import chromadb
router = APIRouter(
    prefix="/query",
    tags=["query"]
)    
llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo-0125")
@router.get("/")
def query_openai_agent(query: str, course_name: str):
    try: 
        if course_name not in get_all_course():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")
        vector = get_vector_index(course_name)
        response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.TREE_SUMMARIZE
        )
        query_engine_tools = create_query_engine_tool(vector.as_query_engine(similarity_top_k=3),course_name)
        agent = OpenAIAgent.from_tools(query_engine_tools, verbose=True,llm=llm, response_synthesizer=response_synthesizer)
        response = agent.chat(query)
        
        return str(response)
    except Exception as e:
          raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
   






















# chroma_client = chromadb.PersistentClient(path="../chroma_db")
# #add db_name for the course
# @router.get("/")
# def query(query: str):
#     try:
#         agents = {}
#         names = chroma_client.list_collections()
#         collections = [collection.name for collection in names]
#         for collection in collections:
#             #also add db to specify the collection
#             vector = create_vector_engine(collection)
#             summary = create_summary_engine(collection)
#             tools = create_engine_tools(vector,summary,collection)
#             agent = create_document_agent(tools,collection)
#             agents[collection] = agent
#         all_tools = convert_tool_agent(collections,agents)
#         obj_index = create_object_index(all_tools)
#         #chat_history1 =  get_chat_history("user")
#         top_agent = fnRetriever(obj_index)
#         #chat_history = chat_history1
#         response = top_agent.chat(query)
#         return str(response)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

# #add db_name for the course
# @router.get("/atlas")
# def query_atlas(query: str, subject:str, user: str ="user"):

#     try:
        
#         agents = {}
        
#         collections = get_collections(subject)
#         print(collections)
#         if not collections:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subject found")
        
#         for collection in collections:
#             #also add db to specify the collection
#             vector = create_vector_engine_atlas(collection,subject)
#             summary = create_summary_engine_atlas(collection,subject)
#             tools = create_engine_tools(vector,summary,collection)
#             agent = create_document_agent(tools,collection)
#             agents[collection] = agent
#         all_tools = convert_tool_agent(collections,agents)
#         obj_index = create_object_index(all_tools)
#         #chat_history1 =  get_chat_history("user")
#         user_conversation = ChatHistory(subject=subject,user_id=user)
#         top_agent = fnRetriever(obj_index)
#         #chat_history = chat_history1
#         response = top_agent.chat(query, user_conversation.get_chat_history())
#         user_conversation.add_message(query,str(response))
#         return str(response)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")