from fastapi import FastAPI
from redis import Redis
import json
from fastapi.responses import JSONResponse

app = FastAPI()

redis_client = Redis(host='localhost', port=6379)

MAX_ENTRIES = 5

CACHE_KEY = "cached_urls_list"

#EXPIRY_TIME = 86400    # 24 * 60 * 60 /set up expirey time for 24 hrs(should be seconds)

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = Redis(host='localhost', port=6379)

@app.on_event("shutdown")
async def shutdown_event():
    redis_client.close()

@app.post('/add-url')
async def add_url(url: str):
    cache_size = redis_client.llen(CACHE_KEY)
    if cache_size >= MAX_ENTRIES:
        redis_client.rpop(CACHE_KEY)   # If cache limit reached, remove the oldest(ie,from the bottom).
    redis_client.lpush(CACHE_KEY, url) #add url to cache.
    #redis_client.expire(CACHE_KEY, EXPIRY_TIME) #setting expiry time as 24 hrs.
    response_data = {
        "Status_code": 200,
        "message": "URL added to cache"
    }
    return JSONResponse(content=response_data)
    #return {"message": "URL added to cache"}
@app.get('/cache')
async def get_cache():
    cached_url = redis_client.lrange(CACHE_KEY,0,-1)
    cached_json_urls = [url.decode() for url in cached_url]
    response_data = {
        "Status_code": 200,
        "message": "success",
        "cached_urls": cached_json_urls
    }
    return JSONResponse(content=response_data)
    #return {"cached_urls": cached_json_urls}

    
    