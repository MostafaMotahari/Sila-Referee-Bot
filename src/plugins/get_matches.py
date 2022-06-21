"""This plugin get matches DAILY from api and save them to database"""

import json
import os
import requests

from datetime import datetime
from decouple import config
from pyrogram.client import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis_om import Migrator

from src.redis.models import MatchModel, MatchImage, RefereeModel, MatchDayModel
from src.plugins.confirm_matches import send_confirm_matches

# Static variables
api_url = config("API_URL")
api_token = config("API_TOKEN")
id_controler = os.environ.get('ID_CONTROLER', 0)


# Check if match exist in database
def check_match_exist(match_id):
    """Check if match exist in database"""

    return True if MatchModel.find(MatchModel.id == match_id).all() else False


# Check if matches are available
def check_matches_available(bot_client: Client):
    """Check if matches are available"""

    headers = {'Authorization': f'Token {api_token}'}
    response = requests.get(f'{api_url}/matches/', headers=headers)

    Migrator().run()
    
    if response.status_code == 200:
        matches = json.loads(response.text)
        match_day = MatchDayModel().find("date", datetime.now().date().strftime("%Y-%m-%d"))
        
        match_day = MatchDayModel(
            id=id_controler,
            date=datetime.now().date().strftime("%Y-%m-%d")
        ) if not match_day else match_day

        os.environ["ID_CONTROLER"] = 

        for match in matches:
            if not check_match_exist(match['id']):
                match_day = save_new_matches(match, match_day)

        send_confirm_matches(bot_client, match_day.id)


# Get match images from api
def save_new_matches(match_json: dict, match_day: MatchDayModel):
    """Get matches save them to database"""

    # Create match images
    match_images = []

    for match_image in match_json['match_images']:
        image = MatchImage(**match_image)
        match_images.append(image)
        image.save()

    # Create match model
    match_model = MatchModel(
        id=match_json['id'],
        match_images=match_images,
        referee=RefereeModel(**match_json['referee']),
        league=match_json['league'],
        home_team=match_json['home_team'],
        away_team=match_json['away_team'],
        tournament=match_json['tournament'],
        starts_at=match_json['starts_at']
    )
    # Save match model
    match_model.save()

    # Save match day model
    match_day.match_models.append(match_model)
    match_day.save()


# Cancel matches
def cancel_matches(match_day_id: str):
    """Cancel matches"""

    match_day = MatchDayModel.find("id", match_day_id).delete()

# scheduler = AsyncIOScheduler()
# scheduler.add_job(get_matches, 'interval', days=1)
# scheduler.start()