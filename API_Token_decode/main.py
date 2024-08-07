from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
#from datetime import datetime, timedelta

app = FastAPI()

class Token(BaseModel):
    token: str

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

@app.post("/decode_token")
async def decode_token(token: Token):
    try:
        payload = jwt.decode(token.token, SECRET_KEY,ALGORITHM)
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401,detail="Token Expired")

