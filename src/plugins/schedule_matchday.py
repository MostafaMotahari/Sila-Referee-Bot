"""This plugin schedule matches of a matchday if it confirmed by owner."""

from datetime import datetime, timedelta
import time
import json

from decouple import config
from pyrogram.client import Client
from pyrogram.types import Message
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import utc

from src.sql.models import MatchDayModel, MatchModel
from src.sql.session import get_db
from src.plugins import message_templates
from src.plugins.refereeing_matches import schedule_referee

# Env variables
api_url = config("API_URL")
api_token = config("API_TOKEN")

jobstores = {
    'default': SQLAlchemyJobStore(url=config('DB_URL'))
}
executors = {
    'default': ThreadPoolExecutor(20),
}
job_defaults = {
    # 'coalesce': False,
    'max_instances': 3,
    # 'misfire_grace_time': 15*60
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone="Asia/Tehran")

# Scheduler
def matchday_scheduler(client: Client, message: Message, match_day_id: int):
    # Get matches of matchday from database
    headers = {'Authorization': f'Token {api_token}'}

    db_session = get_db().__next__()
    match_day: MatchDayModel = db_session.query(MatchDayModel).filter(MatchDayModel.id == match_day_id).first()

    # Schedule send stadium link to players
    for match in match_day.match_objects:
        # Change time of match to local time server
        your_country_time = json.loads(requests.get("http://worldtimeapi.org/api/timezone/" + config("TIME_ZONE")).text)
        your_country_time = datetime.strptime(your_country_time["datetime"].split("T")[0] + " " \
            + your_country_time["datetime"].split("T")[1].split(".")[0], '%Y-%m-%d %H:%M:%S') # Edit here later

        # Skip expired matches
        if your_country_time > match.starts_at:
            continue

        home_team_json = json.loads(requests.get(f'{api_url}/teams/{match.home_team}', headers=headers).text)
        away_team_json = json.loads(requests.get(f'{api_url}/teams/{match.away_team}', headers=headers).text)

        stadium = home_team_json["stadium"]
        stadium_link = client.get_chat(int(stadium["telegram_chat_id"])).invite_link

        # Schedule linking
        for player in home_team_json["players"] + away_team_json["players"]:
            try:
                client.send_message(
                    chat_id = player["user_telegram_id"],
                    text = message_templates.linking_message_template.format( match.starts_at, stadium_link ),
                    # schedule_date = local_match_time - timedelta(hours=0, minutes=20)
                )
            except Exception as e:
                print(e)
                continue

        scheduler.add_job(schedule_referee, trigger='date', run_date=match.starts_at, args=(
            match,
            int(stadium["telegram_chat_id"]),
            home_team_json,
            away_team_json
        ))
    
    scheduler.start()