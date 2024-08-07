
------------------------------------------------------------------------------------
@app.post('/v1/add_family_user')
async def adding_family_user(familyuser: FamilyUser = Body(..., embed=True)):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    existing_main_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    main_user = collection_users.find_one({"Family_id": familyuser.Family_id})
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")

    try:
        if family_user_counter >= 4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
        
        family_user_counter += 1
        
        result = collection_users.insert_one(familyuser.dict())

        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Family user added successfully",
            "user_id": str(result.inserted_id)
        }
        print(f"Users with Family_id {familyuser.Family_id}: {list(collection_users.find({'Family_id': familyuser.Family_id}))}")
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding family user: {str(e)}")
        raise HTTPException(status_code=500, detail="internal server error")
--------------------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import status, Body
import logging

app = FastAPI()

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "Admin_user"
MONGO_COLLECTION_NAME1 = "Users"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]
collection_users = db[MONGO_COLLECTION_NAME1]

logger = logging.getLogger(__name__)

class AdminUser(BaseModel):
    Username: str
    Password: str
    Type: str

class MainUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = Field(..., description="Type cannot be null")

class FamilyUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = "FU"

family_user_counter = 0 #initialize counter for family_id
    
@app.post('/v1/add_admin_user', status_code=status.HTTP_200_OK)
async def adding_admin_user(Admin_user: AdminUser):
    username1 = Admin_user.Username
    password = Admin_user.Password
    types = Admin_user.Type
    if not username1:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "username cannot be empty"})
    if not password:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "password cannot be empty"})
    if not types:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "type cannot be empty"})
    existing_user = collection.find_one({"Username": Admin_user.Username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")
        
    try:
        admin_user_dict = Admin_user.dict()
        result = collection.insert_one(admin_user_dict)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Added admin user successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post('/v1/add_main_user')
async def adding_main_user(main_user: MainUser = Body(..., embed=True)): 
    email = main_user.Email
    password = main_user.Password
    types = main_user.Type
    if not email or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")
    existing_main_user = collection_users.find_one({"Email": main_user.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    try:
        result = collection_users.insert_one(main_user.dict())
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": str(result.inserted_id),  # Convert ObjectId to string
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding main user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal server error")
    
@app.post('/v1/add_family_user')
async def adding_family_user(familyuser: FamilyUser = Body(..., embed=True)):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    existing_main_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    main_user = collection_users.find_one({"Family_id",familyuser.Family_id})
    
    existing_family_users = collection_users.count_documents({"_id": familyuser.Family_id})
    if existing_family_users >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
        
    try:
        result = collection_users.insert_one(familyuser.dict())
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Family user added successfully",
            "user_id": str(result.inserted_id)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding family user: {str(e)}")
        raise HTTPException(status_code=500, detail="internal server error")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
-------------------------------------final with UUid----------------------------------------------------
from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse
from fastapi import status,Body
import logging
import uuid


app = FastAPI()


MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "Admin_user"
MONGO_COLLECTION_NAME1 = "Users"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]
collection_users = db[MONGO_COLLECTION_NAME1]

logger = logging.getLogger(__name__)


class AdminUser(BaseModel):
    Username: str
    Password: str
    Type: str
class MainUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = Field(..., description="Type cannot be null")
    Family_id: str
class FamilyUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = "FU"
    Family_id: str
   
family_user_counter = 0 #initialize counter for family_id
    
@app.post('/v1/add_admin_user',status_code=status.HTTP_200_OK)
async def adding_admin_user(Admin_user:AdminUser):
    username1 = Admin_user.Username
    password = Admin_user.Password
    types = Admin_user.Type
    if not username1:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "username cannot be empty"})
    if not password:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "password cannot be empty"})
    if not types:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "type cannot be empty"})
    existing_user = collection.find_one({"Username": Admin_user.Username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
        
    try:
        admin_user_dict = Admin_user.dict()
        result = collection.insert_one(admin_user_dict)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Added admin user successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post('/v1/add_main_user')
async def adding_main_user(main_user:MainUser = Body(..., embed=True)): 
    email = main_user.Email
    password = main_user.Password
    types = main_user.Type
    if not email or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    main_user.Family_id = str(uuid.uuid4())
    existing_main_user = collection_users.find_one({"Email": main_user.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    try:
        #main_user.Family_id = str(uuid.uuid4())
        #existing_main_user = collection_users.find_one({"Email": main_user.Email})
        #if existing_main_user:
        #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        result = collection_users.insert_one(main_user.dict())
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": str(result.inserted_id),  # Convert ObjectId to string
            "Family_id": main_user.Family_id
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")
    
    
@app.post('/v1/add_family_user')
async def adding_family_user(familyuser:FamilyUser = Body(...,embed=True)):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    existing_family_users = collection_users.count_documents({"Family_id": familyuser.Family_id})
    if existing_family_users >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
    existing_main_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    main_user = collection_users.find_one({"Family_id": familyuser.Family_id})
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")
    
    
        
    family_user_counter = family_user_counter + 1
    try:
    
        result = collection_users.insert_one(familyuser.dict())
        print(family_user_counter)

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
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)
---------------------------email-validation-----------------------------------------------------------
pip install email-validator
 try:
        # Validate the email address
        validate_email(email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
----------------------------------userplans-----------------------------------------------------------------------
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timedelta

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database"]
user_plans_collection = db["User_plans"]

# Pydantic model for user plan data
class UserPlan(BaseModel):
    user_id: str
    current_plans: str
    expiry_date: datetime

# Endpoint to add user plan
@app.post("/add_user_plan")
async def add_user_plan(user_plan: UserPlan = Body(...)):
    # Check if the user ID already exists in the collection
    if user_plans_collection.count_documents({"user_id": user_plan.user_id}) > 0:
        raise HTTPException(status_code=400, detail="User plan already exists")

    # Convert expiry_date to UTC datetime if not already
    if user_plan.expiry_date.tzinfo is None or user_plan.expiry_date.tzinfo.utcoffset(user_plan.expiry_date) is None:
        user_plan.expiry_date = user_plan.expiry_date.replace(tzinfo=datetime.timezone.utc)

    # Insert user plan data into the collection
    user_plan_dict = user_plan.dict()
    user_plans_collection.insert_one(user_plan_dict)

    return {"message": "User plan added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
-----------------------------------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database"]
pricing_collection = db["DNSFilterPricing"]

# Pydantic model for pricing data
class DNSFilterPricing(BaseModel):
    plan_name: str
    price: float
    description: str

# Endpoint to add DNS filter pricing
@app.post("/add_dns_filter_pricing")
async def add_dns_filter_pricing(pricing: DNSFilterPricing = Body(...)):
    # Check if the plan name already exists in the collection
    if pricing_collection.count_documents({"plan_name": pricing.plan_name}) > 0:
        raise HTTPException(status_code=400, detail="Plan with this name already exists")

    # Insert pricing data into the collection
    pricing_dict = pricing.dict()
    pricing_collection.insert_one(pricing_dict)

    return {"message": "DNS filter pricing added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
-----------------------------------------------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field, constr, confloat
from pymongo import MongoClient
import logging

app = FastAPI()

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "your_database_name"
MONGO_COLLECTION_NAME = "plans"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

logger = logging.getLogger(__name__)

class Plan(BaseModel):
    Plan_name: constr(min_length=1, max_length=100)
    Price: confloat(ge=0)
    Features: constr(min_length=1)

@app.post("/add_plan")
async def add_plan(plan: Plan = Body(...)):
    try:
        existing_plan = collection.find_one({"Plan_name": plan.Plan_name})
        if existing_plan:
            raise HTTPException(status_code=400, detail="Plan with this name already exists")
        
        plan_data = plan.dict()
        result = collection.insert_one(plan_data)
        plan_id = str(result.inserted_id)
        return {"message": "Plan added successfully", "plan_id": plan_id}
    except Exception as e:
        logger.error(f"Error adding plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
----------------------------------------------plan purchasing--------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import status, Body
import logging
from datetime import datetime, timedelta

app = FastAPI()

# MongoDB connection details
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "Users"
MONGO_USER_PLANS_COLLECTION_NAME = "User_plans"

# Initialize MongoDB client and collections
client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection_users = db[MONGO_COLLECTION_NAME]
collection_user_plans = db[MONGO_USER_PLANS_COLLECTION_NAME]

# Logging setup
logger = logging.getLogger(__name__)


class Plan(BaseModel):
    Plan_name: str
    Price: float
    Features: str
    Subscription_type: str


class UserPlan(BaseModel):
    User_id: str
    Plan_name: str
    Expiry_date: datetime


@app.post('/purchase_plan')
async def purchase_plan(user_plan: UserPlan):
    # Check if the user exists
    existing_user = collection_users.find_one({"_id": user_plan.User_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Retrieve the plan details
    plan_details = collection_plans.find_one({"Plan_name": user_plan.Plan_name})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan not found")

    # Calculate the expiry date based on the current date and plan duration
    expiry_date = datetime.now() + timedelta(days=30)  # Example: 30 days from now

    # Update the user's plan details in the Users collection
    try:
        result = collection_users.update_one(
            {"_id": user_plan.User_id},
            {"$set": {"Current_plan": user_plan.Plan_name, "Expiry_date": expiry_date}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user plan")
    except Exception as e:
        logger.error(f"Error updating user plan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    # Insert the plan details into the User_plans collection
    try:
        user_plan_data = {
            "User_id": user_plan.User_id,
            "Plan_name": user_plan.Plan_name,
            "Expiry_date": expiry_date
        }
        result = collection_user_plans.insert_one(user_plan_data)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert user plan")
    except Exception as e:
        logger.error(f"Error inserting user plan into User_plans collection: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    # Construct the response
    response_data = {
        "message": "Plan purchased successfully",
        "user_id": user_plan.User_id,
        "plan_name": user_plan.Plan_name,
        "expiry_date": expiry_date
    }
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)
-----------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import status, Body
import logging
from datetime import datetime, timedelta

app = FastAPI()

# MongoDB connection details
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "Users"
MONGO_USER_PLANS_COLLECTION_NAME = "User_plans"

# Initialize MongoDB client and collections
client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection_users = db[MONGO_COLLECTION_NAME]
collection_user_plans = db[MONGO_USER_PLANS_COLLECTION_NAME]

# Logging setup
logger = logging.getLogger(__name__)


class Plan(BaseModel):
    Plan_name: str
    Price: float
    Features: str


class UserPlan(BaseModel):
    User_id: str
    Plan_name: str
    Expiry_date: datetime


@app.post('/purchase_plan')
async def purchase_plan(user_plan: UserPlan):
    # Check if the user exists
    existing_user = collection_users.find_one({"_id": user_plan.User_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Retrieve the plan details
    plan_details = collection_plans.find_one({"Plan_name": user_plan.Plan_name})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan not found")

    # Calculate the expiry date based on the current date and plan duration
    expiry_date = datetime.now() + timedelta(days=30)  # Example: 30 days from now

    # Update the user's plan details in the Users collection
    try:
        result = collection_users.update_one(
            {"_id": user_plan.User_id},
            {"$set": {"Current_plan": user_plan.Plan_name, "Expiry_date": expiry_date}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user plan")
    except Exception as e:
        logger.error(f"Error updating user plan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    # Insert the plan details into the User_plans collection
    try:
        user_plan_data = {
            "User_id": user_plan.User_id,
            "Plan_name": user_plan.Plan_name,
            "Expiry_date": expiry_date
        }
        result = collection_user_plans.insert_one(user_plan_data)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert user plan")
    except Exception as e:
        logger.error(f"Error inserting user plan into User_plans collection: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    # Construct the response
    response_data = {
        "message": "Plan purchased successfully",
        "user_id": user_plan.User_id,
        "plan_name": user_plan.Plan_name,
        "expiry_date": expiry_date
    }
    return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)
-------------------------------------------------------------------------------------------------------
@app.post('/v1/user_plans')
async def user_plans(user_plans: UserPlans):
    user_id = user_plans.User_id
    current_plan = user_plans.Current_plan
    
    # Retrieve the plan details
    plan_details = collection_plans.find_one({"Plan_name": current_plan})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan not found")
    
    # Calculate the expiry date based on the subscription type
    subscription_type = plan_details.get("Subscription_type", "").lower()
    if subscription_type == "monthly":
        expiry_date = datetime.now() + timedelta(days=30)
    elif subscription_type == "yearly":
        expiry_date = datetime.now() + timedelta(days=365)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subscription type")

    # Update the user's plan details in the Users collection
    try:
        result = collection_users.update_one(
            {"_id": user_id},
            {"$set": {"Current_plan": current_plan, "Expiry_date": expiry_date}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user plan")
    except Exception as e:
        logger.error(f"Error updating user plan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    # Construct the response
    response_data = {
        "status_code": status.HTTP_200_OK,
        "message": "User plan updated successfully",
        "user_id": user_id,
        "current_plan": current_plan,
        "expiry_date": expiry_date
    }
    return JSONResponse(content=response_data)
-----------------------------------------final update to users collection----------------------
from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse
from fastapi import status,Body
import logging
from datetime import date, datetime, time, timedelta
from bson import ObjectId
#import uuid


app = FastAPI()


MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME = "Admin_user"
MONGO_COLLECTION_NAME1 = "Users"
MONGO_COLLECTION_NAME_PLANS = "Plans"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]
collection_users = db[MONGO_COLLECTION_NAME1]
collection_plans = db[MONGO_COLLECTION_NAME_PLANS]

logger = logging.getLogger(__name__)


class AdminUser(BaseModel):
    Username: str
    Password: str
    Type: str
class MainUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = Field(..., description="Type cannot be null")
    Family_id: str
class FamilyUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = "FU"
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
   
@app.post('/v1/add_admin_user',status_code=status.HTTP_200_OK)
async def adding_admin_user(Admin_user:AdminUser):
    username1 = Admin_user.Username
    password = Admin_user.Password
    types = Admin_user.Type
    if not username1:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "username cannot be empty"})
    if not password:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "password cannot be empty"})
    if not types:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "type cannot be empty"})
    existing_user = collection.find_one({"Username": Admin_user.Username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
        
    try:
        admin_user_dict = Admin_user.dict()
        result = collection.insert_one(admin_user_dict)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Added admin user successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for adding main user

@app.post('/v1/add_main_user')
async def adding_main_user(main_user:MainUser = Body(..., embed=True)): 
    email = main_user.Email
    password = main_user.Password
    types = main_user.Type
    if not email or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    #main_user.Family_id = str(uuid.uuid4())
    existing_main_user = collection_users.find_one({"Email": main_user.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    try:
        #main_user.Family_id = str(uuid.uuid4())
        #existing_main_user = collection_users.find_one({"Email": main_user.Email})
        #if existing_main_user:
        #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        result = collection_users.insert_one(main_user.dict())
        main_user_id = str(result.inserted_id)
        main_user.Family_id = main_user_id
        collection_users.update_one({"_id": result.inserted_id}, {"$set": {"Family_id": main_user_id}})
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": main_user_id,  # Convert ObjectId to string
            "Family_id": main_user_id
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")
    
# Endpoint for adding family user
   
@app.post('/v1/add_family_user')
async def adding_family_user(familyuser:FamilyUser = Body(...,embed=True)):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    main_user = collection_users.find_one({"Family_id": familyuser.Family_id})
    #print(main_user)
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")
    existing_family_users = collection_users.count_documents({"Family_id": familyuser.Family_id})
    if existing_family_users >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
    existing_main_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
       
    #family_user_counter = family_user_counter + 1
    try:
    
        result = collection_users.insert_one(familyuser.dict())
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
async def plans(pricing:PlansUser = Body(..., embed=True)):
    planname = pricing.Plan_name
    feature = pricing.Features
    if not planname or not feature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    if collection_plans.find_one({"Plan_name":pricing.Plan_name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This plan is already exist")
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
    try:
        userid =ObjectId(userid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    print("User ID:", userid)
    print("User ID Type:", type(userid))
    
    current_plan = user_plans.Current_plan
    plan_details = collection_plans.find_one({"Plan_name":current_plan})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Plan not found")  # Retrieve the plan details
    
    # Calculate the expiry date based on the subscription type
    
    subscription_type = plan_details.get("Subscription_type", "").lower()
    if subscription_type == "monthly":
        expiry_date = datetime.now() + timedelta(days=30)
    elif subscription_type == "yearly":
        expiry_date =datetime.now() + timedelta(days=365)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subscription type")
    
    # Finding the user is existing or not
    
    existing_user = collection_users.find_one({"_id":userid})
    print(existing_user)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    try:
        result = collection_users.update_one(
             {"_id": str(userid)},
             {"$set": {"Current_plan": current_plan, "Expiry_date": expiry_date}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user plan")
    except Exception as e:
        logger.error(f"Error updating user plan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    response_data = {
        "Status_code":status.HTTP_200_OK,
        "Message":"User plan updated successfully",
        "User_id": str(userid),
        "Current_plan": current_plan,
        "Expiry_date": expiry_date
    }
    return JSONResponse(content=response_data)    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)
--------------------------------------------------final before confirmation--------------------------------------------------------
from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse
from fastapi import status,Body
import logging
from datetime import date, datetime, time, timedelta
from bson import ObjectId
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
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = Field(..., description="Type cannot be null")
    Family_id: str
class FamilyUser(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = "FU"
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
   
@app.post('/v1/add_admin_user',status_code=status.HTTP_200_OK)
async def adding_admin_user(Admin_user:AdminUser):
    username1 = Admin_user.Username
    password = Admin_user.Password
    types = Admin_user.Type
    if not username1 or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")
    existing_user = collection.find_one({"Username": Admin_user.Username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
        
    try:
        admin_user_dict = Admin_user.dict()
        result = collection.insert_one(admin_user_dict)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Added admin user successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for adding main user

@app.post('/v1/add_main_user')
async def adding_main_user(main_user:MainUser = Body(..., embed=True)): 
    email = main_user.Email
    password = main_user.Password
    types = main_user.Type
    if not email or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    #main_user.Family_id = str(uuid.uuid4())
    existing_main_user = collection_users.find_one({"Email": main_user.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    try:
        #main_user.Family_id = str(uuid.uuid4())
        #existing_main_user = collection_users.find_one({"Email": main_user.Email})
        #if existing_main_user:
        #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        result = collection_users.insert_one(main_user.dict())
        main_user_id = str(result.inserted_id)
        main_user.Family_id = main_user_id
        collection_users.update_one({"_id": result.inserted_id}, {"$set": {"Family_id": main_user_id}})
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": main_user_id,  # Convert ObjectId to string
            "Family_id": main_user_id
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")
    
# Endpoint for adding family user
   
@app.post('/v1/add_family_user')
async def adding_family_user(familyuser:FamilyUser = Body(...,embed=True)):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    main_user = collection_users.find_one({"Family_id": familyuser.Family_id})
    #print(main_user)
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")
    existing_family_users = collection_users.count_documents({"Family_id": familyuser.Family_id})
    if existing_family_users >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
    existing_main_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
       
    #family_user_counter = family_user_counter + 1
    try:
    
        result = collection_users.insert_one(familyuser.dict())
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
async def plans(pricing:PlansUser = Body(..., embed=True)):
    planname = pricing.Plan_name
    feature = pricing.Features
    if not planname or not feature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    if collection_plans.find_one({"Plan_name":pricing.Plan_name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This plan is already exist")
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
    try:
        userid =ObjectId(userid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    existing_user = collection_user_plans.find_one({"User_id":user_plans.User_id})
    #print(existing_user)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user already exist")
    #print("User ID:", userid)
    #print("User ID Type:", type(userid))
    
    current_plan = user_plans.Current_plan
    if not userid or not current_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    plan_details = collection_plans.find_one({"Plan_name":current_plan})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Plan not found")  # Retrieve the plan details
    
    # Calculate the expiry date based on the subscription type
    
    subscription_type = plan_details.get("Subscription_type", "").lower()
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

------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import status, Body
import logging
from bson import ObjectId

app = FastAPI()

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGO_DB_NAME = "DNS1_FILTER1"
MONGO_COLLECTION_NAME_USERS = "Users"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection_users = db[MONGO_COLLECTION_NAME_USERS]

logger = logging.getLogger(__name__)

class Users(BaseModel):
    Email: str = Field(..., description="Email cannot be null")
    Password: str = Field(..., description="Password cannot be null")
    Type: str = Field(..., description="Type cannot be null")
    Family_id: str = ""

@app.post('/v1/add_main_user')
async def add_main_user(main_user: Users = Body(..., embed=True)):
    email = main_user.Email
    password = main_user.Password
    user_type = main_user.Type
    family_id = main_user.Family_id

    if not email or not password or not user_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")

    if user_type != "MU":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Type must be 'MU' for main user")

    existing_user = collection_users.find_one({"Email": email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    try:
        result = collection_users.insert_one(main_user.dict())
        user_id = str(result.inserted_id)
        if not family_id:
            main_user.Family_id = user_id
            collection_users.update_one({"_id": result.inserted_id}, {"$set": {"Family_id": user_id}})
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": user_id,
            "Family_id": main_user.Family_id
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding main user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@app.post('/v1/add_family_user')
async def add_family_user(family_user: Users = Body(..., embed=True)):
    email = family_user.Email
    password = family_user.Password
    user_type = family_user.Type
    family_id = family_user.Family_id

    if not email or not password or not user_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")

    if user_type != "FU":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Type must be 'FU' for family user")

    if not family_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Family_id is required for family users")

    main_user = collection_users.find_one({"Family_id": family_id})
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")

    existing_family_users = collection_users.count_documents({"Family_id": family_id})
    if existing_family_users >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")

    existing_user = collection_users.find_one({"Email": email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    try:
        result = collection_users.insert_one(family_user.dict())
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Family user added successfully",
            "user_id": str(result.inserted_id)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding family user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
------------------------------------------------------------------------------------------------------------------------------------
from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import status
import logging
from datetime import date, datetime, time, timedelta
from bson import ObjectId
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
class Users(BaseModel):
    Email: str 
    Password: str 
    Type: str 
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
   
@app.post('/v1/add_admin_user',status_code=status.HTTP_200_OK)
async def adding_admin_user(Admin_user:AdminUser):
    username1 = Admin_user.Username
    password = Admin_user.Password
    types = Admin_user.Type
    if not username1 or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")
    existing_user = collection.find_one({"Username": Admin_user.Username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
        
    try:
        admin_user_dict = Admin_user.dict()
        result = collection.insert_one(admin_user_dict)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Added admin user successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for adding main user

@app.post('/v1/add_main_user', response_model= dict)
async def adding_main_user(main_user:Users): 
    email = main_user.Email
    password = main_user.Password
    types = main_user.Type
    familyid = main_user.Family_id
    if not email or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    #main_user.Family_id = str(uuid.uuid4())
    if types != "MU":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Type must be 'MU' for main user")
    existing_main_user = collection_users.find_one({"Email": main_user.Email})
    if existing_main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    try:
        
        result = collection_users.insert_one(main_user.dict())
        user_id = str(result.inserted_id)
        if not familyid:
            main_user.Family_id = user_id
            collection_users.update_one({"_id": result.inserted_id}, {"$set": {"Family_id": user_id}})
        response_data = {
            "Status_code": status.HTTP_201_CREATED,
            "message": "Main user added successfully",
            "user_id": user_id,
            "Family_id": main_user.Family_id
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error adding admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error")
    
# Endpoint for adding family user
   
@app.post('/v1/add_family_user',response_model=dict)
async def adding_family_user(familyuser:Users):
    global family_user_counter
    email = familyuser.Email
    password = familyuser.Password
    types = familyuser.Type
    types_upper = familyuser.Type.upper()
    familyid = familyuser.Family_id
    if not email or not password or not types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields can not be null")
    if types_upper != "FU":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Type must be 'FU' for family user")
    if not familyid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Family_id is required for family users")
        
    main_user = collection_users.find_one({"Family_id": familyuser.Family_id})
    #print(main_user)
    if not main_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Main user not found")
    existing_family_users = collection_users.count_documents({"Family_id": familyuser.Family_id})
    if existing_family_users >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of family users reached")
    existing_user = collection_users.find_one({"Email": familyuser.Email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
       
    #family_user_counter = family_user_counter + 1
    try:
    
        result = collection_users.insert_one(familyuser.dict())
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
    planname = pricing.Plan_name
    feature = pricing.Features
    if not planname or not feature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    if collection_plans.find_one({"Plan_name":pricing.Plan_name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This plan is already exist")
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
    try:
        userid =ObjectId(userid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    existing_user = collection_user_plans.find_one({"User_id":user_plans.User_id})
    #print(existing_user)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user already exist")
    #print("User ID:", userid)
    #print("User ID Type:", type(userid))
    
    current_plan = user_plans.Current_plan
    if not userid or not current_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Fields cannot be null")
    plan_details = collection_plans.find_one({"Plan_name":current_plan})
    if not plan_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Plan not found")  # Retrieve the plan details
    
    # Calculate the expiry date based on the subscription type
    
    subscription_type = plan_details.get("Subscription_type", "").lower()
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
-------------------------------------------------update cache according to time-------------------------------------------------------------------------------------------
@app.get('/v1/redis_cache_users', response_model=dict)
async def get_rediscache_of_users():
    try:
        current_time_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        users = collection_users.find({}, {"_id": 1, "Type": 1, "Family_id": 1})
        for user in users:
            user_id = str(user["_id"])
            user_family_id = user.get("Family_id")
            user_type = user["Type"]
            user_info = {"type": user_type, "family_id": user_family_id}

            default_profile = collection_default_profile.find_one({"user_id": user_id})
            if default_profile:
                profile_id = default_profile.get("profile_id")
                user_info["profile_id"] = profile_id

                profile_rule = collection_profile_rule.find_one({"profile_id": profile_id})
                if profile_rule:
                    category_array = profile_rule.get("category_array", [])
                    user_info["category_array"] = list(category_array)

            last_hit_time_json = redis_client.get(user_id)
            if last_hit_time_json:
                last_hit_time = datetime.strptime(last_hit_time_json.decode('utf-8'), '%Y-%m-%d %H:%M:%S.%f')
                time_difference = datetime.utcnow() - last_hit_time
                if time_difference > EXPIRATION_TIME:
                    # Delete the user from cache if expired
                    redis_client.delete(user_id)
                    redis_client.delete(user_id + "_info")
                else:
                    # If the user is active before expiry, reset the expiry time
                    redis_client.expire(user_id, EXPIRATION_TIME.seconds)
                    redis_client.expire(user_id + "_info", EXPIRATION_TIME.seconds)
            else:
                # Set initial expiry time for user data
                redis_pipeline = redis_client.pipeline()
                redis_pipeline.set(user_id, current_time_str, ex=EXPIRATION_TIME.seconds)
                user_info_with_expiry = user_info.copy()
                user_info_with_expiry["expiry_time"] = current_time_str
                redis_pipeline.set(user_id + "_info", json.dumps(user_info_with_expiry), ex=EXPIRATION_TIME.seconds)
                redis_pipeline.execute()

        response_data = {
            "Status_code": status.HTTP_200_OK,
            "Message": "User data cached successfully"
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error while adding user details to cache: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
