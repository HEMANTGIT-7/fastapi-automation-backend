from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from urllib.parse import quote_plus
from datetime import datetime

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

# ============================================================
# PHONE AUDIT ENDPOINT
# ============================================================

class PhoneAuditRequest(BaseModel):
    number: str
    username: str = "anonymous"


@app.post("/phone-audit", tags=["📱 Phone Audit"])
async def phone_audit(data: PhoneAuditRequest):
    number = data.number.strip()
    
    if not number.startswith("+"):
        raise HTTPException(status_code=400, detail="Number must start with +")
    
    try:
        parsed = phonenumbers.parse(number)
        clean = number.replace("+", "").replace(" ", "").replace("-", "")
        local = clean[2:] if clean.startswith("91") else clean
        with_zero = "0" + local
        
        validation = {
            "valid": phonenumbers.is_valid_number(parsed),
            "country": geocoder.description_for_number(parsed, "en") or "Unknown",
            "carrier": carrier.name_for_number(parsed, "en") or "Unknown",
            "timezone": ", ".join(timezone.time_zones_for_number(parsed)) or "Unknown",
            "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "line_type": str(phonenumbers.number_type(parsed)).replace("PhoneNumberType.", ""),
        }
        
        dorks = []
        dork_list = [
            ("Exact +91", f'intext:"{number}"'),
            ("Without +", f'intext:"{clean}"'),
            ("Local", f'intext:"{local}"'),
            ("With Zero", f'intext:"{with_zero}"'),
            ("Phone Fraud", f'intitle:"Phone Fraud" intext:"{clean}"'),
            ("Pastebin", f'site:pastebin.com "{clean}"'),
            ("PDF Files", f'filetype:pdf "{clean}"'),
            ("Word Files", f'filetype:doc OR filetype:docx "{clean}"'),
            ("Excel Files", f'filetype:xls OR filetype:xlsx "{clean}"'),
            ("GitHub", f'site:github.com "{clean}"'),
            ("LinkedIn", f'site:linkedin.com "{clean}"'),
            ("Facebook", f'site:facebook.com "{clean}"'),
            ("Twitter", f'site:twitter.com "{clean}"'),
            ("Instagram", f'site:instagram.com "{clean}"'),
        ]
        for name, dork in dork_list:
            dorks.append({
                "name": name,
                "url": f"https://www.google.com/search?q={quote_plus(dork)}"
            })
        
        return {
            "status": "success",
            "number": number,
            "timestamp": datetime.now().isoformat(),
            "username": data.username,
            "validation": validation,
            "dorks": dorks,
            "social": {
                "whatsapp": f"https://wa.me/{clean}",
                "telegram": f"https://t.me/+{clean}",
                "truecaller": f"https://www.truecaller.com/search/in/{clean}",
            },
            "breach": {
                "hibp": "https://haveibeenpwned.com",
                "firefox": "https://monitor.firefox.com",
                "leakcheck": "https://leakcheck.io",
            },
            "spam": {
                "truecaller": f"https://www.truecaller.com/search/in/{clean}",
                "findwhocallsme": f"https://findwhocallsme.com/Phone-Number.aspx/{clean}",
                "whocalledme": f"https://who-calledme.com/phone/{clean}",
                "shouldianswer": f"https://www.shouldianswer.com/phone-number/{clean}",
            },
            "privacy_tips": [
                "Number ko social media pe public mat rakho",
                "Truecaller se opt-out karo",
                "2FA lagao har account pe",
                "Har 3 mahine mein audit karo",
            ],
            "legal_warning": "Yeh report sirf apne number ke liye hai. Kisi aur ka number audit karna IT Act 2000 ke under illegal hai."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
