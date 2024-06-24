from typing import Union,List
from pydantic import BaseModel

# Create Models with BaseModel as a parent class

# Position Object
class Position(BaseModel):
    x:float
    y:float

# Style Object
class Style(BaseModel):
    width:int
    height:int

# Node Data
class NodeData(BaseModel):
    label:str

# Node Object
class Node(BaseModel):
    id:str
    type:str
    data:Union[NodeData,None] = None
    width:int
    height:int
    position:Position
    resizing:bool = True
    selected:bool = False
    dragging:bool = False
    positionAbsolute:Position
    style:Union[Style,None] = None
    

# ViewPort Object
class ViewPort(BaseModel):
    x:float
    y:float
    zoom:int =1

# Connection Object
class Edges(BaseModel):
    id:str
    source:str
    sourceHandle:Union[str,None] = None
    target:str
    targetHandle:Union[str,None] = None

# Graph Object
class Graph(BaseModel):
    nodes:Union[List[Node],None] = []
    edges:Union[List[Edges],None] = None
    viewport:ViewPort
        

# Session Object
class Session(BaseModel):
    graph:Graph

# User Details
class User(BaseModel):
    username:str
    password:str="licet@123"
    email_id:str


# view_port = ViewPort(x=12.23,y=34.34)
# graph = Graph(nodes=[],edges=[],viewport=view_port)