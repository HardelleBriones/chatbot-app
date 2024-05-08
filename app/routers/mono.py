from fastapi import Depends, status, HTTPException, Response, APIRouter, UploadFile, File
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
)

import requests
import os

from tempfile import TemporaryDirectory
from services.data_ingestion_services import add_data, format_collection_name
from services.mono_query import (
    get_vector_index, 
    create_agent_mono, add_data_mono, 
    add_file_to_course, delete_file, 
    get_all_files,
    get_all_course,
    delete_course_file,
    get_docstore,
    query_fusion_retriever,
    create_bm25_retriever,
    )
from services.memory_services import ChatHistory
router = APIRouter(
    prefix="/mono",
    tags=["mono"]
)    

@router.get("/query/")
def query_mono(query: str, course_name:str, user: str ="user"):
    try:
        index = get_vector_index(course_name)
        engine = index.as_query_engine()
        agent = create_agent_mono(engine,course_name)
        response = agent.query(query)
        return str(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/query_bm25/")
def query_mono_bm25(query: str, course_name:str, user: str ="user"):
    try:
        if not course_name in get_all_course():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")
        #create vector retriever
        index = get_vector_index(course_name)
        vector_retriever = index.as_retriever(similarity_top_k=2)
        #create bm25 retriever
        docstore = get_docstore(course_name)
        bm25_retriever = create_bm25_retriever(docstore)
        #use fusion retriever
        engine =  query_fusion_retriever(vector_retriever,bm25_retriever)
        agent = create_agent_mono(engine,course_name)

        user_conversation = ChatHistory(subject=course_name,user_id=user)
        
        response = agent.chat(query, user_conversation.get_chat_history(), tool_choice=f"Class_{course_name}")
        user_conversation.add_message(query,str(response))
        return str(response)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred. If this issue persists please contact the admin")


    

@router.delete("/collection/{file_name_to_delete}")
def delete_course_files(course_name: str, file_name_to_delete: str):  
    try:
        if not course_name in get_all_course():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")

        if file_name_to_delete in get_all_files(course_name):
            delete_file(course_name,file_name_to_delete)
            delete_course_file(course_name,file_name_to_delete)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_name_to_delete} not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        # Raise an HTTPException with status code 404 (Not Found) if the course is not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
   

@router.get("/get_files/")
def get_course_files(course_name:str):
    try:
        result = get_all_files(course_name)
        if result:
            return result
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No files or course found")
    except ValueError as e:
        # Raise an HTTPException with status code 404 (Not Found) if the course is not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@router.get("/get_course/")
def get_course():
    try:
        result = get_all_course()
        if result:
            return result
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        # Raise an HTTPException with status code 404 (Not Found) if the course is not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

















    