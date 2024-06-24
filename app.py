import os
from dotenv import load_dotenv
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.redis_db import *
import json
from passlib.context import CryptContext
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

#Connecting to Redis database
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")
redis_db = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# Dummy Route
@app.get("/")
def read_root():
    return {"Hello": "World"}

#Register User
@app.post("/register")
async def register_user(email_id: str, password: str):
    if redis_db.exists(email_id):
        return {"Message":"User already exists"}
    
    hashed_password = pwd_context.hash(password)
    redis_db.hset(email_id, "password", hashed_password)
    return {"Message":"User registered successfully"}

#Authenticate User
@app.post("/authenticate")
async def authenticate_user(email_id: str, password: str):
    if not redis_db.exists(email_id):
         raise {"Message":"User does not exist"}
    
    stored_password = redis_db.hget(email_id, "password")
    if not pwd_context.verify(password, stored_password):
        return {"Message":"Incorrect password"}
    
    return {"Message":"Login successful"}
 
# Save Session Record
@app.post("/save_session")
async def save_session(session_id:str,session_data: dict):
    try:
        db.set(session_id, json.dumps(session_data))
        return {"status":"ok","message":"session saved successfully","userid":session_id}
    except Exception as e:
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

# #Routes_AB
# @app.post("/register")
# async def register_user(user: UserCreate):
#     if redis_db.exists(user.email_id):
#         return {"Message":"User already exists"}
    
#     hashed_password = pwd_context.hash(user.password)
#     redis_db.hset(user.email_id, "password", hashed_password)
#     return {"Message":"User registered successfully"}


# @app.post("/Authenticate")
# async def authenticate_user(user: UserLogin):
#     if not redis_db.exists(user.email_id):
#         return {"Message":"User does not exist"}
    
#     stored_password = redis_db.hget(user.email_id, "password")
#     if not pwd_context.verify(user.password, stored_password):
#         return {"Message":"Incorrect password"}
    
#     return {"Message":"Login successful"}