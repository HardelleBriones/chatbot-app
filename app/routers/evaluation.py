from fastapi import Depends, status, HTTPException, Response, APIRouter, UploadFile, File
from llama_index.core import (
    SimpleDirectoryReader,
)
from llama_index.core.node_parser import SentenceSplitter
import requests
from tempfile import TemporaryDirectory
from services.evaluation_services import file_cost_embeddings

router = APIRouter(
    prefix="/evaluate",
    tags=["evaluate"]
)    
#to be added arg - db_name for the course
@router.post("/filecost/", description="embedding tokens")
async def file_cost(file: UploadFile):
    try:
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
            nodes = SentenceSplitter(chunk_size=120, chunk_overlap=20).get_nodes_from_documents(data)
            tokens =  file_cost_embeddings(nodes)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
