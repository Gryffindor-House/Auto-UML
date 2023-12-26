from typing import Union
from fastapi import FastAPI
from backend.redis_db import *

app = FastAPI()

# Dummy Route
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/insert_record")
async def insert_record(user_id:str,username:str,password:str):
    db.hset(user_id,mapping={'username':username,'password':password})
    return {"Hello":"World"}

@app.get("/get_record")
async def get_record(user_id:str):
    record = db.hgetall(user_id)
    if(record == None):
        return {"error":"user not present"}
    print(record)
    return {"record":record.username}

@app.post("/delete_record")
async def delete_record(user_id:str):
    db.delete(user_id)

@app.post("/authenticate_user")
async def authenticate_user(user_id:str,password:str):
    record = db.hgetall(user_id)
    msg = ""
    if(record == None):
        return 200,{"error":"account not present"}
    else:
        msg = record.password == password

    return {"data":msg}
        