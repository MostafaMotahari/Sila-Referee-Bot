from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    DateTime
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
    image_url = Column(String, index=True)
    image_name = Column(String, index=True)
    image_type = Column(String)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete='CASCADE'))


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    referee = Column(Integer, index=True)
    league = Column(Integer, index=True, nullable=True)
    home_team = Column(Integer)
    away_team = Column(Integer)
    tournament = Column(Integer, nullable=True)
    starts_at = Column(DateTime, index=True)
    match_day_id = Column(Integer, ForeignKey("days.id", ondelete='CASCADE'))
    match_images = relationship("MatchImage", backref="match", passive_deletes=True)


class MatchDayModel(Base):
    __tablename__ = "days"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    match_objects = relationship("MatchModel", backref="match_day", passive_deletes=True)
