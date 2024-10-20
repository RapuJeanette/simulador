from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

client = MongoClient('mongodb://localhost:27017/')
db = client['simulador']

@app.get("/")
def read_root():
    return {"message": "¡Conectado a MongoDB!"}
