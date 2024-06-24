import os
from dotenv import load_dotenv
import uuid
import random

import re

# Loading the env
load_dotenv()

from openai import OpenAI
from langchain_together import ChatTogether

import nltk
from nltk.corpus import stopwords

import json
import warnings

from backend.models import *

# Download Corpus
nltk.download('stopwords')

class Diagram():

	# Data Object
	data_obj = {}

	# Prompt Json
	prompt_json = {}

	# Engines
	openai = None
	together = None

	together_model = "meta-llama/Llama-3-70b-chat-hf"
	# Diagram 

	def __init__(self,user_text,engine="together"):
		self.raw_text = user_text

		# Load Prompts
		self.load_prompts()

		# Generate Graph Instance
		self.graph = Graph(nodes=[],edges=[],viewport=ViewPort(x=302.8159235862322, y=-94.66986803311238))

		self.engine = 	engine

		if(self.engine == "openai"):
			self.openai = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))
		else:
			self.together = ChatTogether(together_api_key=os.getenv("TOGETHER_API_KEY"),model=self.together_model)

	def generate_graph(self):
		self.generate_data_obj()
		return self.graph

	def load_prompts(self):
		with open("./backend/config.json","r+") as f:
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

		if(self.engine == "together"):
			response = ""
			for m in self.together.stream(self.prompt_json['templates']['common']['uml_diagram'].format(USERPROMPT=self.text)):
				response += m.content
			
		elif(self.engine == "openai"):
			# Fetching Name of the UML Diagram
			response = self.openai.chat.completions.create(
					model="gpt-3.5-turbo-1106",
					messages=[{"role": "system", "content":self.prompt_json['templates']['common']['uml_diagram'].format(USERPROMPT=self.text)}],
			)
			response = response.choices[0].message.content

		response = response.lower()

		for key,value in self.prompt_json['diagrams'].items():
			if response in value["synonyms"]:
				self.data_obj['uml_diagram'] = key
				break

	def fetch_problem_statement(self):
		if(self.engine == "together"):
			response = ""
			for m in self.together.stream(self.prompt_json['templates']['common']['problem_statement'].format(USERPROMPT=self.text)):
				response += m.content
			self.data_obj['problem_statement'] = response

		elif(self.engine == "openai"):
			response = self.openai.chat.completions.create(
					model="gpt-3.5-turbo-1106",
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
			self.class_inst = UseCase(self.data_obj,self.graph,engine=self.engine,openai=self.openai,together=self.together)

		self.graph = self.class_inst.generate()

class UseCase():
	prompt_json = None
	def __init__(self,data_obj,graph_inst,engine,openai,together):
		# Assignment data object
		self.data_obj = data_obj

		# Assignment of Graph Instance
		self.graph = graph_inst

		# Assignment of Engine
		self.engine = engine

		# Assignment of OpenAI
		self.openai = openai

		# Assignment of Together
		self.together = together

		# Load prompts
		self.load_prompts()

	def generate(self):
		# Generate Actor Nodes
		self.extract_node_components()
		return self.graph

	def load_prompts(self):
		with open("./backend/config.json","r+") as f:
				self.prompt_json = json.load(f)['templates']['use_case']

	def extract_node_components(self):
		if(self.engine == "together"):
			actor_response = ""  
			for m in self.together.stream(self.prompt_json['actors'].format(PROJECT=self.data_obj['problem_statement'])):
				actor_response += m.content
			actor_names = actor_response.split("\n")[1:-1]
			usecase_response = ""
			for m in self.together.stream(self.prompt_json['usecases'].format(PROJECT=self.data_obj['problem_statement'])):
				usecase_response += m.content
			usecase_names = usecase_response.split("\n")[1:-1]
		
		elif(self.engine == "openai"):
			actor_response = self.openai.chat.completions.create(
					model="gpt-3.5-turbo-1106",
					messages=[{"role": "system", "content":self.prompt_json['actors'].format(PROJECT=self.data_obj['problem_statement'])}],
			)
			actor_names = actor_response.choices[0].message.content.split("\n")[1:-1]
			usecase_response = self.openai.chat.completions.create(
					model="gpt-3.5-turbo-1106",
					messages=[{"role": "system", "content":self.prompt_json['usecases'].format(PROJECT=self.data_obj['problem_statement'])}],
			)
			usecase_names = usecase_response.choices[0].message.content.split("\n")[1:-1]

			

		# Filter out empty strings
		actor_names = list(filter(lambda x:x.strip() != "",actor_names))
		usecase_names = list(filter(lambda x:x.strip() != "",usecase_names))


		if(self.engine == "together"):
			edges_text = ""
			for m in self.together.stream(self.prompt_json['edges'].format(PROJECT=self.data_obj['problem_statement'],ACTORS=actor_names,USECASES=usecase_names)):
				edges_text += m.content
			edges_text = edges_text.split(",")[1:-1]

		self.graph.edges = self.generate_edges(edges_text)
		self.nodes = self.generate_node_data(actor_names,"Actor") + self.generate_node_data(usecase_names,"Oval")
		self.graph.nodes = self.nodes

	def generate_edges(self,edges_text):
		# Generate Edges
		edges = []
		print(edges_text)
		for edge in edges_text:
			edge = edge.split("->")
			edge_data = {
				"id": f"Edge_{uuid.uuid4().hex}",
				"source": edge[0].strip().lower().replace(" ","_"),
				"sourceHandle": "right",
				"target": edge[1].strip().lower().replace(" ","_"),
				"targetHandle": "left"
			}
			edges.append(edge_data)
		return edges

	def generate_node_data(self,components,d_type):
			nodes = []
			used_positions = list()

			for actor_name in components:
					# Generate a unique node ID
					node_id = actor_name.lower().replace(" ", "_")
					
					# Generate a unique position
					position = self.generate_unique_position(used_positions)

					node_data = {
							"id": node_id,
							"dragging": False,
							"height": 130,
							"data": {
									"label": actor_name
							},
							"position": position,
							"positionAbsolute": position,
							"selected": True,
							"type": d_type,
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
	
