import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    print("DATABASE_URL successfully loaded:", DATABASE_URL)
else:
    print("DATABASE_URL not found. Make sure .env exists and has the correct variable.")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Add this function here
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()