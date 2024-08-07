from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from fastapi import status
import logging
import json
from datetime import datetime,timedelta
from bson import ObjectId
from bson.errors import InvalidId
from redis import Redis
app = FastAPI()

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME_PROFILE = "profile"
MONGO_COLLECTION_NAME_PROFILE_RULE = "profile_rule"
MONGO_COLLECTION_NAME_DEFAULT_PROFILE = "default_profile"
MONGO_COLLECTION_NAME_USERS = "Users"
MONGO_COLLECTION_NAME_CATEGORY = "category"
MONGO_COLLECTION_NAME_USER_URL = "black_white_url_user"

redis_client = Redis(host='localhost', port=6379)


client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection_profile = db[MONGO_COLLECTION_NAME_PROFILE]
collection_profile_rule = db[MONGO_COLLECTION_NAME_PROFILE_RULE]
collection_default_profile = db[MONGO_COLLECTION_NAME_DEFAULT_PROFILE]
collection_users = db[MONGO_COLLECTION_NAME_USERS]
collection_category = db[MONGO_COLLECTION_NAME_CATEGORY]
collection_black_white_url_user = db[MONGO_COLLECTION_NAME_USER_URL]

logger = logging.getLogger(__name__)

class ProfileCreate(BaseModel):
    user_id: str
    profile_name: str
    

class ProfileRule(BaseModel):
    profile_id: str
    #user_id: str
    category_array: list
    #is_default: str

class UserUrl(BaseModel):
    User_id: str
    URL: str

EXPIRATION_TIME = timedelta(minutes=5)
    
    
# Endpoint for creating profile

@app.post("/v1/create_profiles", response_model=dict)
async def create_profile(profile: ProfileCreate):
    profiles = profile.profile_name.lower()
    userid = profile.user_id
    try:
        user_id_object = ObjectId(profile.user_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid user_id format. It must be a valid ObjectId.")
    if not userid or not profiles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    user = collection_users.find_one({"_id":ObjectId(userid),"Type":"MU"})
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User not autherized to add profiles")
    existing_profile = collection_profile.find_one({"user_id":profile.user_id,"profile_name":profile.profile_name})
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Same profile already exist for this user")
    profile_count = collection_profile.count_documents({"user_id":profile.user_id})
    if profile_count >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Maximum profile limit reached")
    try:
        result = collection_profile.insert_one({"user_id":profile.user_id,"profile_name":profiles})
        response_data = {
            "Status_code" : status.HTTP_201_CREATED,
            "Message": "Profile added to collection successfully",
            "Profile_id": str(result.inserted_id)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error")

# Endpoint to create profile rules

@app.post('/v1/profile_rules',response_model=dict)
async def add_profile_rule(profile_rule:ProfileRule):

    profileid = profile_rule.profile_id
    try:
        profile_id_object = ObjectId(profile_rule.profile_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid profile_id format. It must be a valid ObjectId")
    if not profileid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Field cannot be null")
    if not collection_profile.find_one({"_id": ObjectId(profile_rule.profile_id)}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile1 = collection_profile.find_one({"_id":ObjectId(profile_rule.profile_id)})
    #print("Retrieved Profile Document:", profile1)
    user_id = profile1.get('user_id')
    #print("userid:",user_id)
    user1 = collection_users.find_one({"_id":ObjectId(user_id),"Type": "MU"})
    #print("Retrieved User Document:",user1)
    if not user1 :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not authorized to add profile rules")
    is_default = "F"
    existing_profile1 = collection_profile_rule.find_one({"is_default":"T"})
    if not existing_profile1:
        is_default = "T"
    #else:
    #    is_default = "F"
    existing_profile = collection_profile_rule.find_one({"profile_id":profile_rule.profile_id})
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile_id already exist")
    blocked_categories = []
    for category_id in profile_rule.category_array:
        category = collection_category.find_one({"_id": ObjectId(category_id)})
        if category:
            blocked_categories.append(category["category_name"])
    try:
        profile_rule_data = profile_rule.dict()
        profile_rule_data["is_default"] = is_default
        result = collection_profile_rule.insert_one(profile_rule_data)
        response_data = {
            "Status_code": status.HTTP_200_OK,
            "Message": "Profile rule added successfully",
            "Profile_rule_id": str(result.inserted_id),
            "Blocked_categories": blocked_categories
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding profile rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")
        
# Endpoint to create Default profile

@app.post('/v1/default_profile', response_model=dict)
async def default_profiles(user_id: str):
    try:
        
        user_id_object = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid user_id format. It must be a valid ObjectId")
    main_user = collection_users.find_one({"_id":user_id_object, "Type":"MU"})
    #print("main user=",main_user)
    if not main_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Main user not found")
    family_users = list(collection_users.find({"Family_id": main_user["Family_id"], "Type":"FU"}))
    #print("familyuser=",family_users)
    profiles = list(collection_profile.find({"user_id":user_id}))
    #print("profile=",profiles)
    if not profiles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Profile not found for this user")
    #profile_ids = profiles[0][("_id")]
    #profile_rule1 = collection_profile_rule.find_one({"profile_id":str(profile_ids),"is_default":"T"})
    #print("profile_rule=",profile_rule1)
    #if not profile_rule1:
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no profile rule with default")
    default_profile_id = None
    for profile in profiles:
        profile_rule1 = collection_profile_rule.find_one({"profile_id": str(profile["_id"]), "is_default": "T"})
        if profile_rule1:
            default_profile_id = str(profile["_id"])
            break
    #print("profile_rule=",default_profile_id)
    if not default_profile_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No default profile found for this user")
    existing_default_profile_result = collection_default_profile.find_one({"user_id":str(main_user["_id"]), "profile_id": str(default_profile_id)})
    if existing_default_profile_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Default profile already exists for main user")
    default_profile_result = collection_default_profile.insert_one({"user_id":str(main_user["_id"]),"profile_id":default_profile_id})
    try:
        for familyuser in family_users:
            existing_default_profile_family_user = collection_default_profile.find_one({"user_id": str(familyuser["_id"]), "profile_id": default_profile_id})
            if existing_default_profile_family_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Default profile already exists for family user: {str(familyuser['_id'])}")
            default_profile_result_family_user = collection_default_profile.insert_one({"user_id":str(familyuser["_id"]), "profile_id": default_profile_id})
        response_data = {
        "Status_code": status.HTTP_200_OK,
        "Message": "Default profile for users added successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding default profile for users:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error")
        
     
# Endpoint to add white listed url from user side
@app.post('/v1/add_white_url_by_user', response_model= dict)
async def add_white_url_by_user(user_url : UserUrl):
    try:
        user_id_object = ObjectId(user_url.User_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid user id format")
    user = collection_users.find_one({"_id": user_id_object, "Type":"MU"})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not found or not authorized to add URLs")
    url = user_url.URL
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Field URL cannot be NULL")
    existing_url = collection_black_white_url_user.find_one({"URL": user_url.URL})
    if existing_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="URL already exist")
    try:
        result = collection_black_white_url_user.insert_one({"User_id":str(user_id_object),"URL":user_url.URL,"Type":"W"})
        response_data = {
            "Status_code": status.HTTP_200_OK,
            "Message":"Url added to white list",
            "URL_id":str(result.inserted_id)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding url {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error")
    
# Endpoint to add black listed url from user side

@app.post('/v1/add_black_url_by_user', response_model=dict())
async def add_white_url_by_user(user_url:UserUrl):
    try:
        user_id_object = ObjectId(user_url.User_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid user id format")
    user = collection_users.find_one({"_id":user_id_object, "Type": "MU"})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found or not authorized to add URLs")
    existing_url = collection_black_white_url_user.find_one({"URL":user_url.URL})
    if existing_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Url already exist")
    try:
        result = collection_black_white_url_user.insert_one({"User_id":user_id_object,"URL":user_url.URL,"Type":"B"})
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "Message": "Url added to black list",
            "URL_id": str(result.inserted_id)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding black list url {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error")
    
#Endpoint for Caching details in redis

@app.get('/v1/redis_cache_users',response_model=dict)
async def get_rediscache_of_users():
    try:
        current_time_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        users = collection_users.find({}, {"_id": 1, "Type": 1,"Family_id":1})
        for user in users:
            users_id = str(user["_id"])
            user_family_id = user.get("Family_id")
            user_type = user["Type"]
            user_info = {"type":user_type,"family_id":user_family_id}
            
            default_profile1 = collection_default_profile.find_one({"user_id":users_id})
            if default_profile1:
                profile_id = default_profile1.get("profile_id")
                user_info["profile_id"] = profile_id
                
                profile_rule = collection_profile_rule.find_one({"profile_id":profile_id})
                if profile_rule:
                    category_array = profile_rule.get("category_array",[])
                    user_info["category_array"] = list(category_array)
            
            last_hit_time_json = redis_client.get(users_id)
            if last_hit_time_json:
                last_hit_time = datetime.strptime(last_hit_time_json.decode('utf-8'), '%Y-%m-%d %H:%M:%S.%f')
                a = datetime.utcnow() - last_hit_time
                if a > EXPIRATION_TIME:
                    redis_client.delete(users_id)
                    redis_pipeline.delete(users_id + "_info")
                else:
                    user_info_with_expiry = user_info.copy()
                    user_info_with_expiry["expiry_time"] = last_hit_time_json.decode('utf-8')
                    redis_pipeline = redis_client.pipeline()
                    #redis_pipeline.set(users_id, current_time_str)
                    redis_pipeline.set(users_id, json.dumps(user_info_with_expiry), ex = EXPIRATION_TIME.seconds)
                    redis_pipeline.execute()
            else:
                user_info_with_expiry = user_info.copy()
                user_info_with_expiry["expirey_time"] = current_time_str
                redis_pipeline = redis_client.pipeline()
                #redis_pipeline.set(users_id, current_time_str)
                redis_pipeline.set(users_id, json.dumps(user_info_with_expiry), ex = EXPIRATION_TIME.seconds)
                redis_pipeline.execute()
                    
            #user_info_json = json.dumps(user_info)
            #redis_client.set(users_id,current_time_str)
            #redis_client.set(users_id+ "_info",json.dumps(user_info))
            
        response_data ={
            "Status_code":status.HTTP_200_OK,
            "Message":"User data cached successfully"
            
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding user details in to cache {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error")
    
       
if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)