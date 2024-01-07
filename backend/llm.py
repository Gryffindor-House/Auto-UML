import os
from dotenv import load_dotenv
import uuid
import random

import re

# Loading the env
load_dotenv()

from openai import OpenAI

import nltk
from nltk.corpus import stopwords

import json
import warnings

import yake
kw_extractor = yake.KeywordExtractor(dedupLim=float(os.getenv("DUPLICATION_THRESHOLD")))

openai = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "What color is apple?Respond in a single word"},
#   ]
# )


# Download Corpus
nltk.download('stopwords')

class UseCase:


  diagrams_json = {}
    
  def __init__(self,user_text):
    self.raw_text = user_text

    # Generate Data Object
    self.generate_data_obj()

  def extract_node_components(self,message):
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": message}],
    )
    actor_names = response.choices[0].message.content.split("\n")[1:-1]
    return actor_names

  def generate_node_data(self,components):
      nodes = []
      used_positions = list()

      for actor_name in components:
          node_id = f"Actor_{uuid.uuid4().hex}"
          
          # Generate a unique position
          position = self.generate_unique_position(used_positions)

          node_data = {
              "id": node_id,
              "label": actor_name,
              "dragging": False,
              "height": 130,
              "data": {
                  "label": "Added node"
              },
              "position": position,
              "positionAbsolute": position,
              "selected": True,
              "type": "Actor",
              "width": 74
          }

          nodes.append(node_data)

      return nodes

  def generate_unique_position(self,used_positions, viewport_width=100, viewport_height=100, min_distance=10):
      # Generate a random position, ensuring it's unique, within the viewport, and not too far from existing positions
      while True:
          position = {"x": random.uniform(0, viewport_width), "y": random.uniform(0, viewport_height)}

          # Check if the position is within the viewport
          if 0 <= position["x"] <= viewport_width and 0 <= position["y"] <= viewport_height:
              # Check if the position is not too close to existing positions
              too_close = any(
                  abs(position["x"] - existing["x"]) < min_distance and
                  abs(position["y"] - existing["y"]) < min_distance
                  for existing in used_positions
              )

              if not too_close:
                  used_positions.append(position)
                  return position
            


  def generate_data_obj(self):

    # Removal Special Charaters
    self.text = re.sub('\W+',' ',self.raw_text).strip().lower()
    self.text = re.sub(r'[^a-zA-Z0–9]'," ",self.text)

    # Removal of stopwords
    text_words = list(self.text.split(" "))
    text_words  = list(filter(lambda x:x not in stopwords.words('english'),text_words))

    formatted_text = " ".join(text_words)
    #print(formatted_text)
  
    #print(kw_extractor.extract_keywords(formatted_text))

    keywords = kw_extractor.extract_keywords(formatted_text)
    #print(keywords)

    ## Search for the diagram
    diagrams = ['use case']

    for diagram in diagrams:
      kws = list(filter(lambda x: diagram in x[0],keywords))
      if(len(kws)>0):
        print(diagram)
        break


    #diagram_type = list(filter(lambda x:))


    # Generate Problem Statement
    pass

  

  def generate_edges(actions):
    pass
  
with open("./prompts.json","r+") as f:
  json_file = json.load(f)


inst = UseCase(json_file[0]['prompt'])

# node_data_list = inst.generate_node_data(actor_names)
# for node_data in node_data_list:
#     print(node_data)

# message = '''Sure! Here are some actor names for a bus management system:

# 1. Bus Driver
# 2. Ticket Inspector
# 3. Passenger
# 4. Bus Conductor
# 5. Administrator
# 6. Bus Dispatcher
# 7. Maintenance Staff
# 8. Security Personnel
# 9. Customer Service Representative
# 10. Bus Operator'''
message = "Give me just the names of actors alone for use case of bus management system for UML diagram"

message_call = inst.extract_node_components(message)
print(message_call)