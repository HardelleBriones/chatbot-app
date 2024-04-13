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
import chromadb
router = APIRouter(
    prefix="/collection",
    tags=["collection"]
)    
chroma_client = chromadb.PersistentClient(path="../chroma_db")



@router.get("/")
def collections():
    try:
        names = chroma_client.list_collections()
        collections = [collection.name for collection in names]
        if not collections:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No collections found")
        return collections
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error:{e}") 
    
@router.delete("collection/{collection_name}")
def delete_collection(collection_name: str):
    try:
        names = chroma_client.list_collections()
        collections = [collection.name for collection in names]
        if not collections:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No collections found")
        chroma_client.delete_collection(name=collection_name)
        return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error:{e}") 
@router.put("/change_collection_name")
def change_collection_name(name:CollectionChange):
    try:
        names = chroma_client.list_collections()
        collections = [collection.name for collection in names]
        if not collections:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No collections found")
        collection = chroma_client.get_collection(name=name.old_collection)
        formatted_name = format_collection_name(name.new_collection)
        collection.modify(name=formatted_name)
        return {"message": "Collection name changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error:{e}") 
    

#to be added arg - db_name for the course
@router.post("/uploadfile/", description="Upload file")
async def upload_file(file: UploadFile):
    file_name = file.filename.split('.')[0]
    names = chroma_client.list_collections()
    collections = [collection.name for collection in names]
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
        add_data(formatted, nodes)
    return {"filename": file.filename}

@router.post("/downloadlink/", description="Add file using link")
async def upload_file_link(download_link: str):
    
    # Create a temporary directory using a context manager
    with TemporaryDirectory() as temp_dir:
        try:
            # Download the file from the provided link
            response = requests.get(download_link)
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to download file from the provided link.")
            
            # Extract the filename from the download link
            filename = download_link.split("/")[-1].split(".")[0]
        
            names = chroma_client.list_collections()
            collections = [collection.name for collection in names]
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
            add_data(formatted, nodes)
            return {"filename": filename}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")


#also add endpoint to get all collection on a certain subject
#modify the endpoint of adding knowledge that will format the name based on the db or coursename 
#- course-year-section-teacher(any of this combination so that it will be unique)




    