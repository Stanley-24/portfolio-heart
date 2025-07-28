from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.routes import resume, experience, projects, reviews, newsletter, contact, analytics, auth
from app.routes.email import email
from app.routes.chatbot import chatbot
from app.routes.leads import leads
from app.routes.admin import security
from app.middleware.security_middleware import SecurityMiddleware
from sqlalchemy import create_engine
from app.core.database import Base
import app.models.experience
import app.models.project
import app.models.review
import app.models.newsletter
import app.models.contact
import app.models.resume

# SMTP/Email startup check
required_smtp_vars = [
    'ZOHO_SMTP_SERVER',
    'ZOHO_SMTP_PORT',
    'ZOHO_SMTP_USER',
    'ZOHO_SMTP_PASS',
    'EMAIL_FROM',
]
missing_smtp = [var for var in required_smtp_vars if not os.getenv(var)]
if missing_smtp:
    print(f"[WARNING] Missing SMTP environment variables: {', '.join(missing_smtp)}. Email sending will not work until these are set.")

# Log all environment variables loaded from .env at startup
print("\n[ENVIRONMENT VARIABLES LOADED AT STARTUP]")
for key, value in os.environ.items():
    if key in [
        'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_HOST', 'POSTGRES_PORT',
        'ZOHO_SMTP_SERVER', 'ZOHO_SMTP_PORT', 'ZOHO_SMTP_USER', 'ZOHO_SMTP_PASS', 'EMAIL_FROM'
    ]:
        print(f"{key}={value}")
print()

# Log database connection string (hide password for security)
def safe_db_url(settings):
    url = settings.DATABASE_URL
    if '://' in url:
        parts = url.split('://')
        creds, rest = parts[1].split('@', 1)
        user = creds.split(':')[0]
        return f"{parts[0]}://{user}:***@{rest}"
    return url

print(f"[DATABASE URL] {safe_db_url(settings)}")

# Test database connection at startup
try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("[DATABASE CONNECTION SUCCESSFUL]")
    # Auto-create all tables
    print("[AUTO-CREATING ALL TABLES IF NOT EXIST]")
    Base.metadata.create_all(engine)
    print("[TABLE CREATION COMPLETE]")
except Exception as e:
    print(f"[DATABASE CONNECTION FAILED] {e}")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Stanley Owarieta's Portfolio",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://stanleyowarieta.com",
        "https://stanley-o.vercel.app",
        "http://127.0.0.1:5173",
        "https://portfolio-heart.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(resume.router, prefix=f"{settings.API_V1_STR}/resume", tags=["resume"])
app.include_router(experience.router, prefix=f"{settings.API_V1_STR}/experience", tags=["experience"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["reviews"])
app.include_router(newsletter.router, prefix=f"{settings.API_V1_STR}/newsletter", tags=["newsletter"])
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contact", tags=["contact"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(email.router, prefix="/api/email", tags=["email"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(leads.router, prefix="/api", tags=["leads"])
app.include_router(security.router, prefix="/api/security", tags=["security"])

@app.get("/")
async def root():
    return {
        "message": "Stanley Portfolio API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/api/protected-test")
def protected_test(admin=Depends(auth.get_current_admin)):
    return {"message": "You are authenticated as admin."}

@app.post("/api/protected-test-post")
def protected_test_post(admin=Depends(auth.get_current_admin)):
    return {"message": "You are authenticated as admin (POST)."}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 