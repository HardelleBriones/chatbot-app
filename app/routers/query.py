from fastapi import Depends, status, HTTPException, Response, APIRouter
from services.agent_services import ItemManager
import chromadb
bot = ItemManager()
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
            vector = bot.create_vector_engine(collection)
            summary = bot.create_summary_engine(collection)
            tools = bot.create_engine_tools(vector,summary,collection)
            agent = bot.create_document_agent(tools,collection)
            agents[collection] = agent
        all_tools = bot.convert_tool_agent(collections,agents)
        obj_index = bot.create_object_index(all_tools)
        #chat_history1 =  get_chat_history("user")
        top_agent = bot.fnRetriever(obj_index)
        #chat_history = chat_history1
        response = top_agent.chat(query)
        return str(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")