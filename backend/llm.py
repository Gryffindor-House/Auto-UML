import os
from dotenv import load_dotenv

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

  diagrams_json = {}
    
  def __init__(self,user_text):
    self.raw_text = user_text

    # Generate Data Object
    self.generate_data_obj()

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

  def generate_actors(self):
    pass

  def generate_edges(actions):
    pass
  
with open("./prompts.json","r+") as f:
  json_file = json.load(f)


inst = UseCase(json_file[0]['prompt'])
