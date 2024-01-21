from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.redis_db import *
import json

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

# Dummy Route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Save Session Record
@app.post("/save_session")
async def save_session(session_id:str,session1:Session):
    try:
        sample_text = "Draw a use case diagram for bus management system "
        db.set(session_id,str(session1.model_dump_json()))
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
        # print(graph)

        session1 = Session(session_id=session_id,graph =graph)
        db.set(session_id,str(session1.model_dump_json()))

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