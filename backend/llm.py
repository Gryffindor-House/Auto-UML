import os
from dotenv import load_dotenv

# Loading the envd
load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "What color is apple?Respond in a single word"},
  ]
)

print(response)