from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
from typing import Generator
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)


def create_db_tables():
    """Create all tables on startup."""
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator:
    """
    Dependency — gives each request its own session.
    Automatically closes when request is done.
    """
    with Session(engine) as session:
        yield session