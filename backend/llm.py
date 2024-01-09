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

# Download Corpus
nltk.download('stopwords')

class Diagram():

	# Data Object
	data_obj = {}

	# Prompt Json
	prompt_json = {}

	def __init__(self,user_text):
		self.raw_text = user_text

		# Load Prompts
		self.load_prompts()

		# Generate data object
		self.generate_data_obj()

	def load_prompts(self):
		with open("./config.json","r+") as f:
				self.prompt_json = json.load(f)

	def fetch_diagram(self):
		self.text = self.raw_text
		# Removal Special Charaters
		self.text = re.sub('\W+',' ',self.raw_text).strip().lower()
		self.text = re.sub(r'[^a-zA-Z0–9]'," ",self.text)

		self.data_obj["text"] = self.text
		self.data_obj["raw_tex"] = self.raw_text

		# Removal of stopwords
		text_words = list(self.text.split(" "))
		text_words  = list(filter(lambda x:x not in stopwords.words('english'),text_words))

		# Fetching Name of the UML Diagram
		response = openai.chat.completions.create(
				model="gpt-3.5-turbo",
				messages=[{"role": "system", "content":self.prompt_json['templates']['common']['uml_diagram'].format(USERPROMPT=self.text)}],
		)
		response = response.choices[0].message.content.lower()

		for key,value in self.prompt_json['diagrams'].items():
			if response in value["synonyms"]:
				self.data_obj['uml_diagram'] = key
				break

	def fetch_problem_statement(self):
		response = openai.chat.completions.create(
				model="gpt-3.5-turbo",
				messages=[{"role": "system", "content":self.prompt_json['templates']['common']['problem_statement'].format(USERPROMPT=self.text)}],
		)
		self.data_obj['problem_statement'] = response.choices[0].message.content

	def generate_data_obj(self):
		
		# Fetch Diagram name
		self.fetch_diagram()

		# Fetch Problem Statement
		self.fetch_problem_statement()

		# Assign Class Instance
		if(self.data_obj['uml_diagram'] == 'use_case' ):
			self.class_inst = UseCase(self.data_obj)

		self.class_inst.generate()
		pass

class UseCase():
	prompt_json = None
	def __init__(self,data_obj):
		# Assignment data object
		self.data_obj = data_obj

		# Load prompts
		self.load_prompts()

	def generate(self):
		# Generate Actor Nodes
		self.extract_node_components()
		print(self.nodes)

	def load_prompts(self):
		with open("./config.json","r+") as f:
				self.prompt_json = json.load(f)['templates']['use_case']

	def extract_node_components(self):
		response = openai.chat.completions.create(
				model="gpt-3.5-turbo",
				messages=[{"role": "system", "content":self.prompt_json['actors'].format(PROJECT=self.data_obj['problem_statement'])}],
		)
		actor_names = response.choices[0].message.content.split("\n")[1:-1]

		self.nodes = self.generate_node_data(actor_names)

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
					

	def generate_edges(actions):
		pass
	
with open("./prompts.json","r+") as f:
	json_file = json.load(f)


inst = Diagram(json_file[0]['prompt'])