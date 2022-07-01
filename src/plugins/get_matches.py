"""This plugin get matches DAILY from api and save them to database"""

import json
import requests

from datetime import datetime
from decouple import config
from pyrogram.client import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from sqlalchemy import exists

from src.sql.models import MatchModel, MatchImage, MatchDayModel
from src.sql.session import get_db
from src.plugins.confirm_matches import send_confirm_matches

# Static variables
api_url = config("API_URL")
api_token = config("API_TOKEN")

# Check if match exist in database
def check_match_exist(db_session: Session, match_id):
    """Check if match exist in database"""

    return True if db_session.query(exists().where(MatchModel.id == match_id)).scalar() else False


# Check if matches are available
def check_matches_available(bot_client: Client):
    """Check if matches are available"""

    headers = {'Authorization': f'Token {api_token}'}
    response = requests.get(f'{api_url}/matches/', headers=headers)
    db_session = get_db().__next__()

    
    if response.status_code == 200:
        matches = json.loads(response.text)

        match_day = db_session.query(MatchDayModel).filter(MatchDayModel.date == datetime.now().date().strftime("%Y-%m-%d")).first()

        if not match_day:
            match_day = MatchDayModel(date=datetime.now().date().strftime("%Y-%m-%d"))
            db_session.add(match_day)
            db_session.commit()
            db_session.refresh(match_day)
            match_day = db_session.query(MatchDayModel).filter(MatchDayModel.date == datetime.now().date().strftime("%Y-%m-%d")).first()

        for match in matches:
            if not check_match_exist(db_session, match['id']):
                match_day = save_new_matches(db_session, match, match_day)

        send_confirm_matches(bot_client, match_day.id)


# Get match images from api
def save_new_matches(db_session: Session, match_json: dict, match_day: MatchDayModel):
    """Get matches save them to database"""

    # Create match images
    match_images = []

    for match_image in match_json['match_images']:
        image = MatchImage(
            image_url=match_image["image"],
            image_name=match_image["name"],
            image_type=match_image["type"],
        )
        match_images.append(image)

        db_session.add(image)
        db_session.commit()
        db_session.refresh(image)


    # Create match model
    match_model = MatchModel(
        id=match_json['id'],
        match_images=match_images,
        referee=match_json['referee']['id'],
        league=match_json['league'],
        home_team=match_json['home_team'],
        away_team=match_json['away_team'],
        tournament=match_json['tournament'],
        starts_at=match_json['starts_at'],
        match_day_id=match_day.id,

    )
    # Save match model
    db_session.add(match_model)
    db_session.commit()
    db_session.refresh(match_model)

    # Save match day model
    match_day.match_objects.append(match_model)
    db_session.commit()
    db_session.refresh(match_day)

    return match_day


# Cancel matches
def cancel_matches(match_day_id: str):
    """Cancel matches"""

    MatchDayModel.find(MatchDayModel.id == match_day_id).delete()

# scheduler = AsyncIOScheduler()
# scheduler.add_job(get_matches, 'interval', days=1)
# scheduler.start()
