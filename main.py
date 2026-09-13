from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="⚡ Secure API Portal",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# Single source of truth for features
feature_requests_store = []

# Mutable multi-user database
USER_DATABASE = {
    "HEMANT": "8877",
    "HEMMAD": "HAMMAD@123",
    "HEMANT1": "123",
    "HARIOM": "123",
    "VIP_USER": "secure789"
}

user_data_store = {
    "123456789": {"name": "Player_Alpha", "likes": 50},
    "987654321": {"name": "Player_Beta", "likes": 120}
}

class UserAuthRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class LikeRequest(BaseModel):
    target_uid: str
    count: int

class FeatureRequest(BaseModel):
    username: str
    feature_text: str

@app.get("/")
def home():
    return {"status": "Online", "message": "FastAPI Server is Running Perfectly!"}

# Optional: Add user registration endpoint so new users work dynamically
@app.post("/register-user", tags=["🔑 Authentication System"])
def register_user(data: RegisterRequest):
    user = data.username.strip().upper()
    pwd = data.password.strip()
    USER_DATABASE[user] = pwd
    return {"status": "success", "message": f"User {user} registered!"}

@app.post("/verify-user", tags=["🔑 Authentication System"], summary="Validate EXE App User Credentials")
def verify_user_credentials(auth: UserAuthRequest):
    user = auth.username.strip().upper()
    pwd = auth.password.strip()
    
    if user in USER_DATABASE and USER_DATABASE[user] == pwd:
        return {"status": "success", "message": f"Welcome {user}!", "user": user}
    else:
        raise HTTPException(status_code=401, detail="Invalid Username or Password!")

@app.post("/add-likes", tags=["🚀 Automation Endpoints"])
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

@app.post("/submit-feature", tags=["📝 Feature Requests"])
def submit_feature(data: FeatureRequest):
    req_entry = {"username": data.username, "feature_text": data.feature_text}
    feature_requests_store.append(req_entry)
    print(f"\n[NEW FEATURE REQUEST] From {data.username}: {data.feature_text}\n")
    return {"status": "Success", "message": "Request Received!"}

@app.get("/get-features", tags=["📝 Feature Requests"])
def get_all_features():
    return {"total_requests": len(feature_requests_store), "requests": feature_requests_store}

@app.delete("/clear-features", tags=["📝 Feature Requests"])
def clear_features():
    feature_requests_store.clear()
    return {"status": "cleared"}
