from fastapi import Depends, status, HTTPException, Response, APIRouter, UploadFile, File
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
)
from llama_index.core.node_parser import SentenceSplitter
import requests
import os
from tempfile import TemporaryDirectory
from services.data_ingestion_services import add_data, format_collection_name
from routers.schemas import CollectionChange 
from services.atlas_services import add_data_atlas, get_collections,get_vector_databases, check_database_exists
router = APIRouter(
    prefix="/collection_atlas",
    tags=["collection_atlas"]
)    

@router.get("/subjects/")
def get_subjects():
    try:
        collections = get_vector_databases()
        if not collections:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
        
        return collections
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error:{e}") 

@router.get("/")
def collections(db_name: str):
    try:
        check_db = check_database_exists(db_name)
        if not check_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
        
        collections = get_collections(db_name)
        if not collections:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No collections found")
        
        return collections
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error:{e}") 
        

#to be added arg - db_name for the course
@router.post("/uploadfile/", description="Upload file")
async def upload_file(file: UploadFile, db_name: str):
    file_name = file.filename.split('.')[0]

    collections = get_collections(db_name)
    if file_name in collections:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail=f"{file_name} already exist")


    # Create a temporary directory using a context manager
    with TemporaryDirectory() as temp_dir:
        # Save the uploaded file content to the temporary directory
        temp_file_path = f"{temp_dir}/{file.filename}"
        file_content = await file.read()  # Read the uploaded file content
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)  # Write content to temporary file
        # Process the file using SimpleDirectoryReader with the full path
        data = SimpleDirectoryReader(input_files=[temp_file_path]).load_data()
        #data returns a Document object
        nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=20).get_nodes_from_documents(data)
        formatted = format_collection_name(file_name)
        add_data_atlas(formatted,db_name,nodes)
    return {"filename": file.filename}

@router.post("/downloadlink/", description="Add file using link")
async def upload_file_link(download_link: str, db_name:str):
    
    # Create a temporary directory using a context manager
    with TemporaryDirectory() as temp_dir:
        try:
            # Download the file from the provided link
            response = requests.get(download_link)
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to download file from the provided link.")
            
            # Extract the filename from the download link
            filename = download_link.split("/")[-1].split(".")[0]

            collections = get_collections(db_name)
            if filename in collections:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail=f"{filename} already existss")
            temp_file_path = os.path.join(temp_dir, filename)
            
            # Write the downloaded content to the temporary file
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(response.content)
                
            # Process the file using SimpleDirectoryReader with the full path
            data = SimpleDirectoryReader(input_files=[temp_file_path]).load_data()
            # Assuming add_data is a function to add data to a database or storage
            nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=20).get_nodes_from_documents(data)
            formatted = format_collection_name(filename)
            add_data_atlas(formatted,db_name,nodes)
            return {"filename": filename}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")


