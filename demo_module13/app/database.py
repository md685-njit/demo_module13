from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5434/demo_module11"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)  # Creates demo_users and demo_calculations tables.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
