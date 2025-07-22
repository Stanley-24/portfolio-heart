from sqlalchemy import create_engine, text
from app.core.config import settings

print("DATABASE_URL:", settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar()
        print(f"Connected! PostgreSQL version: {version}")
except Exception as e:
    print(f"Failed to connect: {e}") 