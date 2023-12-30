from fastapi import FastAPI
from backend.redis_db import *
import json

# Import Models
from backend.models import *

# App Route
app = FastAPI()

# Dummy Route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Save Session Record
@app.post("/save_session")
async def save_session(session_id:str,session:Session):
    db.set(session_id,str(session.json()))

# Load Session
@app.get("/get_session")
async def get_session(session_id:str):
    record = db.get(session_id)
    if(record == None):
        return 200,{"error":"Record Not Present"}
    print(record)
    return json.loads(record)

# Clear Data
@app.post("/delete")
async def delete_record(session_id:str):
    db.delete(session_id)

####### AUTHENTICATION ROUTES ########
    
# Register User
@app.post("/register")
async def register_user(user:User):
    db.set(user.email_id,str(user.json()))

# Authenticate User
@app.post("/authenticate")
async def authenticate_user(email_id:str,password:str):
    user_record = json.loads(db.get(email_id))
    if(user_record.password == password):
        return 400,{"msg":"authenticate success"}
    return 400,{"msg":'credentials not valid',"code":200}