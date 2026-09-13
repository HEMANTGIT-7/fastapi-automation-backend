from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel

app = FastAPI(
    title="⚡ Secure API Portal",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)
@app.get("/")
def home():
    return {"status": "Online", "message": "FastAPI Server is Running Perfectly!"}

# Multi-User Database (Aap alag-alag users ki ID aur Pass yahan add kar sakte hain)
USER_DATABASE = {
    "HEMANT": "8877",
    "HEMA": "123",
    "md yaqoob": "y123",
    "hario": "h123",
    
    "VIP_USER": "secure789"
}

user_data_store = {
    "12345": {"name": "Player_Alpha", "likes": 50},
    "987654": {"name": "Player_Beta", "likes": 120}
     "123456": {"name": "Player_Alpha", "likes": 54},
    "987654": {"name": "Player_Beta", "likes": 125}
    "123456": {"name": "Player_Alpha", "likes": 58},
    "987654": {"name": "Player_Beta", "likes": 129}
}

class UserAuthRequest(BaseModel):
    username: str
    password: str

class LikeRequest(BaseModel):
    target_uid: str
    count: int

# Dynamic User Verification Endpoint for EXE App
@app.post("/verify-user", tags=["🔑 Authentication System"], summary="Validate EXE App User Credentials")
def verify_user_credentials(auth: UserAuthRequest):
    user = auth.username.strip().upper()
    pwd = auth.password.strip()
    
    if user in USER_DATABASE and USER_DATABASE[user] == pwd:
        return {"status": "success", "message": f"Welcome {user}!", "user": user}
    else:
        raise HTTPException(status_code=401, detail="Invalid Username or Password!")

@app.post("/add-likes", tags=["🚀 Automation Endpoints"], summary="Free Fire Mass Likes Pipeline")
def add_likes(data: LikeRequest):
    if data.target_uid not in user_data_store:
        user_data_store[data.target_uid] = {"name": f"User_{data.target_uid}", "likes": 0}
    
    user_data_store[data.target_uid]["likes"] += data.count
    return {
        "status": "Success",
        "uid": data.target_uid,
        "added_likes": data.count,
        "total_likes": user_data_store[data.target_uid]["likes"]
    }

# User requests save karne ke liye dictionary / list
feature_requests_store = []

class FeatureRequest(BaseModel):
    username: str
    feature_text: str

@app.post("/submit-feature", tags=["📝 Feature Requests"], summary="Receive Feature Ideas from Users")
def submit_feature(data: FeatureRequest):
    req_entry = {"user": data.username, "request": data.feature_text}
    feature_requests_store.append(req_entry)
    
    # Terminal me Print hoga jab bhi koi user request bhejega
    print(f"\n[NEW FEATURE REQUEST] From {data.username}: {data.feature_text}\n")
    
    return {"status": "Success", "message": "Request Received!"}

# Aap Browser me 'http://127.0.0.1:8000/get-features' khol kar sare requests dekh sakte hain
@app.get("/get-features", tags=["📝 Feature Requests"], summary="View All Submitted Features")
def get_all_features():
    return {"total_requests": len(feature_requests_store), "data": feature_requests_store}
