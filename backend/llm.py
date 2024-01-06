import os
from dotenv import load_dotenv

import re

# Loading the envd
load_dotenv()
from openai import OpenAI

import nltk
from nltk.corpus import stopwords

import json
import warnings

# client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "What color is apple?Respond in a single word"},
#   ]
# )


# Download Corpus
nltk.download('stopwords')

class UseCase:
    
  def __init__(self,user_text):
    self.raw_text = user_text

    # Generate Data Object
    self.generate_data_obj()

  def generate_data_obj(self):

    # Removal Special Charaters
    self.text = re.sub('\W+',' ',self.raw_text)

    # Removal of stopwords
    text_words = list(self.text.split(" "))
    text_words  = list(filter(lambda x:x not in stopwords.words('english'),text_words))

    print(text_words)

    # Generate Problem Statement
    pass

  def generate_actors(self):
    pass

  def generate_edges(actions):
    pass
  
with open("./prompts.json","r+") as f:
  json_file = json.load(f)


inst = UseCase(json_file[0]['prompt'])
