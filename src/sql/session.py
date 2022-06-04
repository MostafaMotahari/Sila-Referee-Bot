from typing import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = os.environ.get("db_url")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    try:
        db = local_session()
        yield db
    finally:
        db.close()