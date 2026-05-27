from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
from typing import Generator
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stockmind.db")

# SQLite needs this extra argument
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_tables():
    SQLModel.metadata.create_all(engine)
    print("Database tables created ✅")


def get_db() -> Generator:
    with Session(engine) as session:
        yield session