from fastapi import status, HTTPException, Response, APIRouter, UploadFile
from llama_index.core import SimpleDirectoryReader
import requests
import os
from tempfile import TemporaryDirectory
import tempfile
from llama_index.core import Document
from services.knowledge_base_services  import add_file_to_course, get_all_files,valid_index_name
from services.ingest_data_services import add_data
from data_definitions.schemas import Text_knowledgeBase
import tempfile
from llama_index.core import Document
router = APIRouter(
    prefix="/ingest_data",
    tags=["ingest_data"]

)

#to be added arg - db_name for the course
@router.post("/uploadfile/", description="Upload file")
async def upload_file(file: UploadFile, course_name: str):
    try:
        if not valid_index_name(course_name):
            raise ValueError("Invalid Index Name")
        file_name = file.filename
        # Create a temporary directory using a context manager
        with TemporaryDirectory() as temp_dir:
            # Save the uploaded file content to the temporary directory
            temp_file_path = f"{temp_dir}/{file.filename}"
            file_content = await file.read()  # Read the uploaded file content
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)  # Write content to temporary file
            # Process the file using SimpleDirectoryReader with the full path
            data = SimpleDirectoryReader(input_files=[temp_file_path]).load_data()

            #check if file exist
            file = get_all_files(course_name)
            if file_name in file:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")
            
            add_data(course_name, data)
            add_file_to_course(course_name,file_name)
        return Response(status_code=status.HTTP_200_OK, content="Successfully added to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/downloadlink/", description="Add file using link")
async def upload_file_link(download_link: str, course_name:str):
  """
  Downloads a file from the specified URL and stores it in a temporary directory.

  Args:
      url (str): The URL of the file to download.

  Returns:
      str: The path to the downloaded file or None if there was an error.
  """
  if not valid_index_name(course_name):
            raise ValueError("Invalid Index Name")
  # Create a temporary directory
  with tempfile.TemporaryDirectory() as tmpdir:
    # Extract filename from URL, considering the possibility of query parameters
    filename = download_link.split("/")[-1].split("?")[0]  # Get last part before '?'
    #prefixed_filename = f"Topic {topic}-{filename}"  # Add the prefix

    filepath = os.path.join(tmpdir, filename)
   

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
        #nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=20).get_nodes_from_documents(data)
        file_name = data[0].metadata['file_name']

        #check if file exist
        file = get_all_files(course_name)
        if file_name in file:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")
        
        add_data(course_name, data)
        add_file_to_course(course_name,file_name)
        
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    



@router.post("/add_text_knowledge_base/", description="Add text to knowledge base")
async def add_text_knowledge_base(course_name:str, metadata:Text_knowledgeBase):
    try:  
        if not valid_index_name(course_name):
            raise ValueError("Invalid Index Name")
        file_name = metadata.topic
      
         #check if file exist
        file = get_all_files(course_name)
        if file_name in file:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")


        document = Document(
        
        text=metadata.text,
        metadata={
            "file_name": file_name,
            "topic": metadata.topic,
            "description":metadata.description,
            "common_questions":metadata.common_questions,
        },
        excluded_llm_metadata_keys=['file_name'],
        excluded_embed_metadata_keys=['file_name'],
        metadata_seperator="::",
        metadata_template="{key}=>{value}",
        text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
        
        add_data(course_name, [document])
        add_file_to_course(course_name,file_name)
        return Response(status_code=status.HTTP_200_OK, content="Successfully added to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
   