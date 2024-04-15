from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import user, auth, question, meal, generation_responses, train_and_predict

# from .config import settings

# print(settings.database_username)

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# origins = ["https://www.google.com"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)
 

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(question.router)
app.include_router(meal.router)
app.include_router(generation_responses.router)
app.include_router(train_and_predict.router)



@app.get("/")
def root():
    return {"message": "Hello World"}
