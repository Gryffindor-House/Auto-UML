import os
from dotenv import load_dotenv

# Loading the envd
load_dotenv()

import redis

db = redis.Redis(
  host=os.getenv("HOST"),
  port=os.getenv("PORT"),
  password=os.getenv("PASSWORD"))

print("redis connected")