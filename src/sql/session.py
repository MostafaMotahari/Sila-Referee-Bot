import os
from typing import Generator

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = config('DB_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    try:
        db = local_session()
        yield db
    finally:
        db.close()