from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis import Redis
from pymongo import mongo_client

app = FastAPI()

redis_client = Redis(host="localhost",port=6739)

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = ""

client = mongo_client(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = Redis(host="localhost",port=6739)
@app.on_event("shutdown")
async def shutdown_event():
    redis_client.close()
    