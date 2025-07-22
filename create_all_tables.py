from app.core.config import settings
from app.core.database import Base, engine
import app.models.experience
import app.models.project
import app.models.review
import app.models.newsletter
import app.models.contact
import app.models.resume

if __name__ == "__main__":
    print("Creating all tables in the database...")
    Base.metadata.create_all(engine)
    print("Done!") 