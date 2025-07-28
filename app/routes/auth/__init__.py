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
from app.services.email_service import send_password_reset_email_with_zoho

SECRET_KEY = "supersecretkey"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ADMIN_EMAIL = "owarieta24@gmail.com"
ADMIN_PASSWORD = "admin123"

router = APIRouter()

# Use a mutable object to allow password change in-memory
global_admin_password = {"value": ADMIN_PASSWORD}

# In-memory storage for reset tokens (in production, use database)
reset_tokens = {}

# Request models
class ResetPasswordRequest(BaseModel):
    email: str

class ResetPasswordConfirmRequest(BaseModel):
    token: str
    new_password: str

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
    print(f"[DEBUG] get_current_admin called with token: {token}")
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

@router.post("/reset-password", summary="Reset Admin Password")
def reset_password(request: ResetPasswordRequest):
    """Send reset password email to admin"""
    print(f"[DEBUG] Reset password requested for: {request.email}")
    print(f"[DEBUG] ADMIN_EMAIL is: {ADMIN_EMAIL}")
    
    if request.email.lower() != ADMIN_EMAIL.lower():
        print(f"[DEBUG] Email mismatch - returning early")
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset link has been sent.", "success": True}
    
    try:
        print(f"[DEBUG] Email matches - proceeding with reset")
        # Generate a secure reset token
        import secrets
        reset_token = secrets.token_urlsafe(32)
        print(f"[DEBUG] Generated token: {reset_token[:10]}...")
        
        # Store token with expiration (1 hour from now)
        expiration = datetime.utcnow() + timedelta(hours=1)
        reset_tokens[reset_token] = {
            "email": request.email,
            "expires": expiration
        }
        print(f"[DEBUG] Token stored with expiration: {expiration}")
        
        # Create reset URL (in production, use your actual frontend URL)
        base_url = os.getenv("FRONTEND_URL", "https://portfolio-heart.vercel.app")
        # Force the correct URL if the environment variable is wrong
        if "stanley-o.vercel.app" in base_url:
            base_url = "https://portfolio-heart.vercel.app"
            print(f"[DEBUG] Corrected base URL to: {base_url}")
        reset_url = f"{base_url}/admin/reset-password?token={reset_token}"
        print(f"[DEBUG] Reset URL: {reset_url}")
        print(f"[DEBUG] Base URL from env: {os.getenv('FRONTEND_URL', 'NOT SET')}")
        
        # Send the email
        print(f"[DEBUG] Attempting to send email...")
        try:
            send_password_reset_email_with_zoho(request.email, reset_token, reset_url)
            print(f"[DEBUG] Email sent successfully!")
        except Exception as email_error:
            print(f"[DEBUG] Email sending failed: {email_error}")
            print(f"[DEBUG] Email error type: {type(email_error)}")
            import traceback
            print(f"[DEBUG] Email error traceback: {traceback.format_exc()}")
            # Still return success to user for security, but log the error
            return {"message": "If the email exists, a reset link has been sent.", "success": True}
        
        return {"message": "If the email exists, a reset link has been sent.", "success": True}
        
    except Exception as e:
        print(f"[DEBUG] Error sending reset email: {e}")
        print(f"[DEBUG] Error type: {type(e)}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        # Don't reveal internal errors to user
        return {"message": "If the email exists, a reset link has been sent.", "success": True}

@router.post("/reset-admin", summary="Reset Admin Credentials (testing only)")
def reset_admin():
    global ADMIN_EMAIL
    ADMIN_EMAIL = "owarieta24@gmail.com"
    global_admin_password["value"] = "admin123"
    return {"message": "Admin credentials reset.", "success": True}

@router.post("/reset-password-confirm", summary="Confirm Password Reset")
def reset_password_confirm(request: ResetPasswordConfirmRequest):
    """Confirm password reset with token and new password"""
    if request.token not in reset_tokens:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    token_data = reset_tokens[request.token]
    
    # Check if token has expired
    if datetime.utcnow() > token_data["expires"]:
        # Remove expired token
        del reset_tokens[request.token]
        raise HTTPException(status_code=400, detail="Reset token has expired.")
    
    # Validate new password
    if not request.new_password or len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    
    # Update the password
    global_admin_password["value"] = request.new_password
    
    # Remove the used token
    del reset_tokens[request.token]
    
    return {"message": "Password reset successfully.", "success": True}

@router.get("/reset-password-verify", summary="Verify Reset Token")
def verify_reset_token(token: str):
    """Verify if a reset token is valid"""
    if token not in reset_tokens:
        raise HTTPException(status_code=400, detail="Invalid reset token.")
    
    token_data = reset_tokens[token]
    
    # Check if token has expired
    if datetime.utcnow() > token_data["expires"]:
        # Remove expired token
        del reset_tokens[token]
        raise HTTPException(status_code=400, detail="Reset token has expired.")
    
    return {"message": "Token is valid.", "success": True} 

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