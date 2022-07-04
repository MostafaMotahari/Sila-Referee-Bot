"""This plugin get matches DAILY from api and save them to database"""

from email import message
import json
import requests

from datetime import datetime
from decouple import config
from pyrogram.types import Message
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from sqlalchemy import exists

from src.sql.models import MatchModel, MatchImage, MatchDayModel
from src.sql.session import get_db
from src.plugins import confirm_matches

# Static variables
api_url = config("API_URL")
api_token = config("API_TOKEN")

# Check if match exist in database
def check_match_exist(db_session: Session, match_id):
    """Check if match exist in database"""

    return True if db_session.query(exists().where(MatchModel.id == match_id)).scalar() else False


# Check if matches are available
def check_matches_available(message: Message):
    """Check if matches are available"""

    headers = {'Authorization': f'Token {api_token}'}
    response = requests.get(f'{api_url}/matches/', headers=headers)
    db_session = get_db().__next__()

    
    if response.status_code == 200:
        matches = json.loads(response.text)

        if not db_session.query(exists().where(MatchDayModel.date == datetime.now().date().strftime("%Y-%m-%d"))).scalar():
            match_day = MatchDayModel(date=datetime.now().date().strftime("%Y-%m-%d"))
            db_session.add(match_day)
            db_session.commit()
            db_session.refresh(match_day)

        match_day = db_session.query(MatchDayModel).filter(MatchDayModel.date == datetime.now().date().strftime("%Y-%m-%d")).first()


        new_match_detected = False
        for match in matches:
            if not check_match_exist(db_session, match['id']):
                match_day = save_new_matches(db_session, match, match_day)
                new_match_detected = True
        else:
            if new_match_detected:
                confirm_matches.send_confirm_matches(message, match_day.id)

            else:
                message.edit("♻️ No matches avalable.")


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
def cancel_matches(match_day_id: int):
    """Cancel matches"""

    db_session = get_db().__next__()
    db_session.query(MatchDayModel).filter(MatchDayModel.id == match_day_id).delete()
    db_session.commit()

# Set an scheduler for checking new mathches
# scheduler = BackgroundScheduler()
# scheduler.add_job(check_matches_available, 'interval', days=1, args=(__main__.app, ))
# scheduler.start()
