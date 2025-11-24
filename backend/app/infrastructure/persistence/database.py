from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# La base de datos está en la carpeta 'frontend', al mismo nivel que 'backend'
# BASE_DIR es backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# PROJECT_ROOT es la raíz del workspace
PROJECT_ROOT = os.path.dirname(BASE_DIR)
# DB_PATH apunta a frontend/db.sqlite3
DB_PATH = os.path.join(PROJECT_ROOT, "frontend", "db.sqlite3")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
