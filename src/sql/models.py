from operator import index
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.sql.base import Base

# Model classes

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    telegram_id = Column(Integer, unique=True, index=True)


class MatchImage(Base):
    __tablename__ = "match_images"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    image_url = Column(String, unique=True, index=True)
    image_name = Column(String, unique=True, index=True)
    image_type = Column(String)


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_images = relationship("MatchImage", backref="match")
    referee = Column(Integer, index=True)
    league = Column(Integer, index=True, nullable=True)
    home_team = Column(Integer, index=True)
    away_team = Column(Integer, index=True)
    tournament = Column(Integer, index=True, nullable=True)
    starts_at = DateTime(index=True)