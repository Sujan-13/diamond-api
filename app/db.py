import os
from typing import Annotated
from datetime import datetime, UTC
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, Column, JSON
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(ENV_PATH)

class DiamondLogBase(SQLModel):
    query: dict = Field(default_factory=dict, sa_column=Column(JSON))
    probability: float
    cut: str

class DiamondLog(DiamondLogBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at : datetime = Field(default_factory=lambda: datetime.now(UTC))

class DiamondLogPublic(DiamondLogBase):
    id: int

db_url = os.getenv("DATABASE_URL", f"sqlite:///diamond_logs.db" )

engine = create_engine(db_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

