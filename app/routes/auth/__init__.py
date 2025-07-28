from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
import os
import json
from fastapi.responses import RedirectResponse
from fastapi import Request
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel

SECRET_KEY = "supersecretkey"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ADMIN_EMAIL = "owarieta24@gmail.com"
ADMIN_PASSWORD = "admin123"

router = APIRouter()

# Use a mutable object to allow password change in-memory
global_admin_password = {"value": ADMIN_PASSWORD}

# Request models
class ForgotPasswordRequest(BaseModel):
    email: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", summary="Admin Login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username.lower() != ADMIN_EMAIL.lower() or form_data.password != global_admin_password["value"]:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": ADMIN_EMAIL, "role": "admin"})
    return {"access_token": access_token, "token_type": "bearer", "success": True}

# Dependency for protected endpoints
def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub").lower() != ADMIN_EMAIL.lower() or payload.get("role") != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return payload

@router.post("/change-password", summary="Change Admin Password")
def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    admin=Depends(get_current_admin)
):
    if old_password != global_admin_password["value"]:
        raise HTTPException(status_code=400, detail="Old password is incorrect.")
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    
    global_admin_password["value"] = new_password
    return {"message": "Password changed successfully.", "success": True}

@router.post("/quick-change-password", summary="Quick Change Admin Password (No Auth Required)")
def quick_change_password(
    email: str = Body(...),
    new_password: str = Body(...),
    secret_key: str = Body(...)
):
    """Quick password change for admin (requires secret key)"""
    # Verify email matches admin
    if email.lower() != ADMIN_EMAIL.lower():
        raise HTTPException(status_code=400, detail="Invalid email address.")
    
    # Verify secret key (you can change this to any secret you want)
    expected_secret = "stanley_admin_2024"
    if secret_key != expected_secret:
        raise HTTPException(status_code=400, detail="Invalid secret key.")
    
    # Validate new password
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    
    # Update password
    global_admin_password["value"] = new_password
    return {"message": "Password changed successfully.", "success": True}

@router.post("/create-admin", summary="Create Admin Account")
def create_admin(email: str = Body(...), password: str = Body(...)):
    global ADMIN_EMAIL
    if global_admin_password["value"] != ADMIN_PASSWORD or ADMIN_EMAIL != "owarieta24@gmail.com":
        return {"message": "Admin account already exists.", "success": False}
    if not email or not password or len(password) < 6:
        return {"message": "Email and password (min 6 chars) are required.", "success": False}
    ADMIN_EMAIL = email
    global_admin_password["value"] = password
    return {"message": "Admin account created successfully.", "success": True}



@router.post("/reset-admin", summary="Reset Admin Credentials (testing only)")
def reset_admin():
    global ADMIN_EMAIL
    ADMIN_EMAIL = "owarieta24@gmail.com"
    global_admin_password["value"] = "admin123"
    return {"message": "Admin credentials reset to default (admin123).", "success": True}

@router.post("/forgot-password", summary="Forgot Password - Reset to Default")
def forgot_password(request: ForgotPasswordRequest):
    """Reset password to default when user forgets password"""
    if request.email.lower() != ADMIN_EMAIL.lower():
        return {
            "message": "Invalid email address. Please enter the correct admin email.", 
            "success": False
        }
    
    # Reset to default password
    global_admin_password["value"] = "admin123"
    
    return {
        "message": "Password has been reset to default. You can now login with the default password.", 
        "success": True,
        "default_password": "admin123"
    }

 

@router.get("/google-oauth-login", summary="Start Google OAuth2 login for calendar access")
def google_oauth_login():
    client_id = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
    redirect_uri = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/api/auth/google-oauth-callback")
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": [redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri=redirect_uri
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    return RedirectResponse(auth_url)

@router.get("/google-oauth-callback", summary="Handle Google OAuth2 callback")
def google_oauth_callback(request: Request):
    client_id = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
    redirect_uri = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/api/auth/google-oauth-callback")
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": [redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri=redirect_uri
    )
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    # Save credentials to a file (token.json)
    token_dir = "app/credentials"
    os.makedirs(token_dir, exist_ok=True)
    with open(os.path.join(token_dir, "token.json"), "w") as token:
        token.write(credentials.to_json())
    return {"message": "Google Calendar authentication successful! You can now create events with invites."} 