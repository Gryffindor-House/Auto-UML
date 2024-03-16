import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.redis_db import *
import json
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List,Union
from fastapi import Depends

# Import Models
from backend.models import *

# Importing llm module
from backend.llm import *

# App Route
app = FastAPI()

# Add the dev url of front end
origins = [
    "localhost:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Connecting to PostgreSQL database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


#Define SQLAlchemyBase
Base = declarative_base()

#User model
class User_db(Base):
    __tablename__ = "users"
    #id = Column(Integer,primary_key=True,index=True)
    email_id = Column(String,primary_key=True)
    password = Column(String)

#Create the table
Base.metadata.create_all(bind=engine)

#Hiding the password
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

#Pydantic model for user
class UserCreate(BaseModel):
    email_id: str
    password: str

class UserLogin(BaseModel):
    email_id: str
    password: str



# Dummy Route
@app.get("/")
def read_root():
    return {"Hello": "World"}
 
# Save Session Record
@app.post("/save_session")
async def save_session(session_id:str,session1:Session):
    try:
        db.set(session_id,str(session1.json()))
        return {"status":"ok","message":"session saved successfully","userid":session_id}
    except Exception as e:
        print(e)
        return {"status":"NOK","message":"server error"}

# Generate graph
@app.post("/generate_graph")
async def generate_graph(session_id:str,user_text:str):
    try:
        diag_inst = Diagram(user_text)
        graph= diag_inst.generate_graph()

        session1 = Session(session_id=session_id,graph =graph)
        db.set(session_id,str(session1.json()))

        return {"status":"OK","message":"graph generated successfully"}

    except Exception as e:
        print(e)
        return {"status":"NOK","message":"server error"}

# Load Session
@app.get("/get_session")
async def get_session(session_id:str):
    record = db.get(session_id)
    # print(json.loads(record))
    if(record == None):
        return 200,{"error":"Record Not Present"}
    return json.loads(record)

# Clear Data
@app.post("/delete")
async def delete_record(session_id:str):
    db.delete(session_id)
    return {"status":"ok","message":"record deleted successfully"}

####### AUTHENTICATION ROUTES ########
    
# Register User
# @app.post("/register")
# async def register_user(user:User_db):
#     db.set(user.email_id,str(user.json()))

# Authenticate User
# @app.post("/authenticate")
# async def authenticate_user(email_id:str,password:str):
#     user_record = json.loads(db.get(email_id))
#     if(user_record.password == password):
#         return 400,{"msg":"authenticate success"}
#     return 400,{"msg":'credentials not valid',"code":200}

#Routes_AB
@app.post("/register")
async def register_user(user: UserCreate):
    db_user = SessionLocal()
    hashed_password = pwd_context.hash(user.password)
    user_record = User_db(email_id=user.email_id,password=hashed_password)
    db_user.add(user_record)
    db_user.commit()
    db_user.refresh(db_user)
    return {"Message":"User registered successfully"}

@app.post("/Authenticate")
async def authenticate_user(user: UserLogin):
    db_user = SessionLocal()
    result = db_user.query(User_db).filter(User_db.email_id == user.email_id).first()
    if result is None:
        return {"Message":"User not found"}
    if not pwd_context.verify(user.password,result.password):
        return {"Message":"Incorrect password"}
    return {"Message":"Login successful"}