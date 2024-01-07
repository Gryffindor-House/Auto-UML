import os
from dotenv import load_dotenv
import uuid
import random

# Loading the envd
load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "Give me just the names of actors alone for use case of bus management system"},
  ]
)

print(response.choices[0].message.content)
message = '''Sure! Here are some actor names for a bus management system:

1. Bus Driver
2. Ticket Inspector
3. Passenger
4. Bus Conductor
5. Administrator
6. Bus Dispatcher
7. Maintenance Staff
8. Security Personnel
9. Customer Service Representative
10. Bus Operator'''

def extract_node_components(message):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": message}],
    )
    actor_names = response.choices[0].message.content.split("\n")[1:-1]
    return actor_names

def generate_node_data(components):
    nodes = []
    used_positions = list()

    for actor_name in components:
        node_id = f"Actor_{uuid.uuid4().hex}"
        
        # Generate a unique position
        position = generate_unique_position(used_positions)

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

def generate_unique_position(used_positions, viewport_width=100, viewport_height=100, min_distance=10):
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
            
# Example usage:
actor_names = [
    "Bus Driver", "Ticket Inspector", "Passenger",
    "Bus Conductor", "Administrator", "Bus Dispatcher",
    "Maintenance Staff", "Security Personnel", "Customer Service Representative",
    "Bus Operator"
]

node_data_list = generate_node_data(actor_names)
for node_data in node_data_list:
    print(node_data)