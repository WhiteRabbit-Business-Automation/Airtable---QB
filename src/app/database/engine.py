from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import SQLALCHEMY_DATABASE_URL

# Use SQLite-specific connect_args only when using sqlite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
