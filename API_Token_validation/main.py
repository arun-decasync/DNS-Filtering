from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta

app = FastAPI()

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "user"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

class UserCredentials(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str

SECRET_KEY = "whhjzxkhzjjz12"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(username: str):
    user_doc = collection.find_one({"username": username})
    if user_doc:
        return dict(user_doc)
    else:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

@app.post("/token")
async def generate_token(credentials: UserCredentials):
    user = get_user(credentials.username)
    if user and user["password"] == credentials.password:
        token_expiry = datetime.utcnow() + timedelta(minutes=1) 
        payload = {"sub": credentials.username, "exp": token_expiry}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return Token(access_token=token)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/validate-token")
async def validate_token(current_user: dict = Depends(get_current_user)):
    return {"message": "Token is valid"}
