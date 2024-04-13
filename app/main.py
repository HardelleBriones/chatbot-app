from fastapi import FastAPI, UploadFile
#from . import models
# from .database import engine
from routers import query, knowledge_base, user, evaluation
#models.Base.metadata.create_all(bind=engine)
app = FastAPI()




app.include_router(query.router)
app.include_router(knowledge_base.router)
app.include_router(user.router)
app.include_router(evaluation.router)



