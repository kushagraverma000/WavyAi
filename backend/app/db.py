from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_database_backend() -> str:
    url = settings.database_url
    lower = url.lower()
    if lower.startswith("postgresql"):
        return "postgresql"
    if lower.startswith("sqlite"):
        return "sqlite"
    return "unknown"
