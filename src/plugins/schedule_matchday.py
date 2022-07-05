"""This plugin schedule matches of a matchday if it confirmed by owner."""

from datetime import datetime, timedelta
from dateutil import tz

from decouple import config
from pyrogram.client import Client
from pyrogram.types import Message
import requests
import json

from src.sql.models import MatchDayModel, MatchModel
from src.sql.session import get_db
from src.plugins import message_templates

api_url = config("API_URL")
api_token = config("API_TOKEN")

# Scheduler
def matchday_scheduler(client: Client, message: Message, match_day_id: int):
    # Get matches of matchday from database
    headers = {'Authorization': f'Token {api_token}'}

    db_session = get_db().__next__()
    match_day: MatchDayModel = db_session.query(MatchDayModel).filter(MatchDayModel.id == match_day_id).first()

    # Schedule send stadium link to players
    for match in match_day.match_objects:
        # Change time of match to local time server
        local_match_time = datetime.fromisoformat(match.starts_at).astimezone(tz.tzlocal()) #.strftime('%Y-%m-%d %H:%M:%S')

        home_team_json = json.loads(requests.get(f'{api_url}/teams/{match.home_team}', headers=headers))
        away_team_json = json.loads(requests.get(f'{api_url}/teams/{match.away_team}', headers=headers))

        stadium = home_team_json["stadium"]
        stadium_link = client.get_chat(stadium["telegram_chat_id"]).invite_link

        # Schedule linking
        for player in home_team_json["players"] + away_team_json["players"]:
            try:
                client.send_message(
                    chat_id = player["user_telegram_id"],
                    text = message_templates.linking_message_template.format( match.starts_at, stadium_link ),
                    schedule_date = local_match_time - timedelta(hours=0, minutes=20)
                )
            except Exception as e:
                print(e)
                continue