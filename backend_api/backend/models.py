from typing import Union,List
from pydantic import BaseModel

# Create Models with BaseModel as a parent class



# Node Object
class Node(BaseModel):
    id:str
    type:str
    label:str
    pos_x:int
    pos_y:int

# Connection Object
class Connection(BaseModel):
    conn_id:str
    source:str
    destination:str

# Graph Object
class Graph(BaseModel):
    graph_type:str
    nodes:List[Node]
    description:Union[None,str]=None
    connections:Union[List[Connection],None] = None

# Session Object
class Session(BaseModel):
    user_id:str
    graph:Graph

# User Details
class User(BaseModel):
    username:str
    password:str="licet@123"
    email_id:str
