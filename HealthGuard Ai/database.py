# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔹 CHANGE THESE according to your MySQL setup
DB_USER = "root"          # your MySQL username
DB_PASSWORD = "root123"  # your MySQL password
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "healthguard_ai"   # same name as in Workbench

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,          # shows SQL in console (good for debugging)
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency for FastAPI routes (we'll use this later)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
