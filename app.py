from fastapi import FastAPI

app = FastAPI()

# Dummy Route
@app.get("/")
def read_root():
    return {"Hello": "World"}


