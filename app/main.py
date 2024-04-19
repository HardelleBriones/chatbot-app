from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
#from . import models
# from .database import engine
from routers import query, knowledge_base, user, evaluation, atlas, moodle
#models.Base.metadata.create_all(bind=engine)

from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],  # Add OPTIONS method
    allow_headers=["*"],
)




app.include_router(query.router)
app.include_router(moodle.router)
app.include_router(atlas.router)
app.include_router(knowledge_base.router)
app.include_router(user.router)
app.include_router(evaluation.router)