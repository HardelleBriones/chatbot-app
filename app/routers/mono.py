from fastapi import Depends, status, HTTPException, Response, APIRouter, UploadFile, File
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
)
import tempfile

from llama_index.core.node_parser import SentenceSplitter
import requests
import os
from tempfile import TemporaryDirectory
from services.data_ingestion_services import add_data, format_collection_name
from services.mono_query import create_vector_engine_atlas_mono, create_agent_mono, add_data_mono
from routers.schemas import CollectionChange 
from services.atlas_services import add_data_atlas, get_collections,get_vector_databases, check_database_exists
router = APIRouter(
    prefix="/mono",
    tags=["mono"]
)    

@router.get("/")
def query_mono(query: str, course_name:str, user: str ="user"):
    try:
        engine = create_vector_engine_atlas_mono(course_name)
        agent = create_agent_mono(engine,course_name)
        response = agent.query(query)
        return str(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")


    


@router.post("/downloadlink/", description="Add file using link")
async def upload_file_link(download_link: str, course_name:str,topic:str):
  """
  Downloads a file from the specified URL and stores it in a temporary directory.

  Args:
      url (str): The URL of the file to download.

  Returns:
      str: The path to the downloaded file or None if there was an error.
  """
  # Create a temporary directory
  with tempfile.TemporaryDirectory() as tmpdir:
    # Extract filename from URL, considering the possibility of query parameters
    filename = download_link.split("/")[-1].split("?")[0]  # Get last part before '?'
    prefixed_filename = f"Topic {topic}-{filename}"  # Add the prefix

    filepath = os.path.join(tmpdir, prefixed_filename)
   

    # Send a GET request to download the file
    try:
      response = requests.get(download_link, stream=True)
      response.raise_for_status()  # Raise an exception for unsuccessful downloads
    except requests.exceptions.RequestException as e:
      print(f"Error downloading file: {e}")
      return None
    try:
        # Write the downloaded data to the temporary file
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        data = SimpleDirectoryReader(input_files=[filepath]).load_data()
        nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=20).get_nodes_from_documents(data)
        add_data_mono(course_name, nodes)
        return filepath
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")





















    