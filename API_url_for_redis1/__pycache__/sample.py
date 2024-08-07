from fastapi import FastAPI
from redis import Redis
import httpx
import json

app = FastAPI()

whitelist = {
    "www.google.com",
    "www.microsoft.com"
}

@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis(host='localhost',port=6379)
    app.state.http_client = httpx.AsyncClient()
    
@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()

@app.get('/entries1')
async def read_item():
    value = app.state.redis.get('entries')
    if value is None:
        data = {}
        for url in whitelist:
            response = await app.state.http_client.get(url)
            if response.status_code == 200:
                data[url] = response.json()

        data_str = json.dumps(data)
        app.state.redis.set("entries", data_str)
    else:
        data = json.loads(value)

    return data