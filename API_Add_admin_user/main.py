from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import status
import logging
from datetime import date, datetime, time, timedelta
from bson import ObjectId
from email_validator import validate_email,EmailNotValidError

#import uuid


app = FastAPI()


MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "Admin_user"
MONGO_COLLECTION_NAME1 = "Users"
MONGO_COLLECTION_NAME_PLANS = "Plans"
MONGO_COLLECTION_NAME_USER_PLANS = "User_plans"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]
collection_users = db[MONGO_COLLECTION_NAME1]
collection_plans = db[MONGO_COLLECTION_NAME_PLANS]
collection_user_plans =db[MONGO_COLLECTION_NAME_USER_PLANS]

logger = logging.getLogger(__name__)


class AdminUser(BaseModel):
    Username: str
    Password: str
    Type: str
class MainUser(BaseModel):
    Email: str
    Password: str 
    #Type: str = "MU" 
    #Family_id: str
class FamilyUser(BaseModel):
    Email: str 
    Password: str 
    #Type: str = "FU"
    Family_id: str
class UserPlans(BaseModel):
    User_id: str
    Current_plan: str
    #Expirey_date: datetime
class PlansUser(BaseModel):
    Plan_name: str
    Price: float
    Features: str
    Subscription_type: str
   
family_user_counter = 0 #initialize counter for family_id

#Endpoint for adding admin user
   
@app.post('/v1/add_admin_user', response_model= dict)
async def adding_admin_user(Admin_user:AdminUser):
    username1 = Admin_user.Username
    password = Admin_user.Password
    types = Admin_user.Type.upper()
    if not username1 or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")
    if types not in ["AU","FC","DEO"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid value for Type. It must be either 'AU','FC' or 'DEO'")
    existing_user = collection.find_one({"Username": Admin_user.Username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
        
    try:
        result = collection.insert_one({"Username":username1,"Password":password,"Type":types})
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Added admin user successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for adding main user

@app.post('/v1/add_main_user',response_model=dict)
async def adding_main_user(main_user:MainUser): 
    email = main_user.Email
    password = main_user.Password
    #types = main_user.Type
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    #main_user.Family_id = str(uuid.uuid4())
    try:
        validate_email(email)
    except EmailNotValidError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid email id")
    existing_main_user = collection_users.find_one({"Email": main_user.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    try:
        result = collection_users.insert_one({"Email":main_user.Email,"Password":main_user.Password,"Type":"MU"})
        main_user_id = str(result.inserted_id)
        #main_user.Family_id = main_user_id
        collection_users.update_one({"_id": result.inserted_id}, {"$set": {"Family_id": main_user_id}})
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": main_user_id, 
            "Family_id": main_user_id
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")
    
# Endpoint for adding family user
   
@app.post('/v1/add_family_user',response_model=dict)
async def adding_family_user(familyuser:FamilyUser):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    try:
        validate_email(email)
    except EmailNotValidError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid email id")
    main_user = collection_users.find_one({"Family_id": familyuser.Family_id,"Type":"MU"})
    #print(main_user)
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")
    existing_family_users = collection_users.count_documents({"Family_id": familyuser.Family_id,"Type":"FU"})
    if existing_family_users >= 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
    existing_main_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
       
    #family_user_counter = family_user_counter + 1
    try:
    
        result = collection_users.insert_one({"Email":familyuser.Email,"Password":familyuser.Password,"Type":"FU","Family_id":familyuser.Family_id})
        #print(family_user_counter)

        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Family user added successfully",
            "user_id": str(result.inserted_id)
        }
        #print(f"Users with Family_id {familyuser.Family_id}: {list(collection_users.find({'Family_id': familyuser.Family_id}))}")
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding family user: {str(e)}")
    raise HTTPException(status_code=500,detail="internal server error")

# Endpoint to add plans from admin

@app.post('/v1/plans_for_users')
async def plans(pricing:PlansUser):
    planname = pricing.Plan_name.lower()
    feature = pricing.Features
    type = pricing.Subscription_type
    type1 = type.lower()
    if not planname or not feature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    if planname not in ["basic","pro","advanced"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid value for plan . It must be either 'basic','pro' or 'advanced'.")
    if collection_plans.find_one({"Plan_name":pricing.Plan_name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This plan is already exist")
    if type1 not in ["monthly","yearly"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid value for subscription type. It must be either 'monthly' or 'yearly'.")
    try:
        
        result = collection_plans.insert_one(pricing.dict())
        response_data = {
            "status_code": status.HTTP_201_CREATED,
            "message": "Plans for user added successfully",
            "plan_id": str(result.inserted_id)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while addinng Plans for user: {str(e)}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")

# Endpoint for User purchasing a plan

@app.post('/v1/user_plans')
async def user_plans(user_plans:UserPlans):
    userid = user_plans.User_id
    current_plan = user_plans.Current_plan
    try:
        userid =ObjectId(userid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    if not userid or not current_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    mainuser = collection_users.find_one({"_id":ObjectId(userid),"Type":"MU"})
    if not mainuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not authorized to purchase plan")
    existing_user = collection_user_plans.find_one({"User_id":user_plans.User_id})
    #print(existing_user)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exist")
    plan_details = collection_plans.find_one({"Plan_name":current_plan})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Plan not found")  # Retrieve the plan details
    
    # Calculate the expiry date based on the subscription type
    
    subscription_type = plan_details.get("Subscription_type")
    if subscription_type == "monthly":
        expiry_date = datetime.now() + timedelta(days=30)
    elif subscription_type == "yearly":
        expiry_date =datetime.now() + timedelta(days=365)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subscription type")
    
    # Finding the user is existing or not
    try:
        usplan = {
            "User_id": str(userid),
            "Current_plan": current_plan,
            "Expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        result = collection_user_plans.insert_one(usplan)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store user plan")
                    
    except Exception as e:
        logger.error(f"Error updating user plan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    response_data = {
        "Status_code":status.HTTP_200_OK,
        "Message":"User plan updated successfully",
        "User_id": str(userid),
        "Current_plan": current_plan,
        "Expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    }
    return JSONResponse(content=response_data)    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)