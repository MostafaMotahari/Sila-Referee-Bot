import os
import time
import json

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from decouple import config
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from src.plugins import message_templates
from src.sql.models import MatchModel
from src.plugins import goal_checker


# Seprate session for scheduled tasks
# Env variables
api_url = config("API_URL")
api_token = config("API_TOKEN")

app = Client(
    "SilaScheduleBot",
    api_id=config("API_ID"),
    api_hash=config("API_HASH"),
    bot_token=config("BOT_TOKEN"),
)

temp_memory = {
    "score_board_id": None,
    "picture": {
        "id": None,
        "type": None,
        "name": None,
        "number": 0
    }
}

schedular = BackgroundScheduler()


# Send picture function
def send_image_match(match: MatchModel, stadium_id, number_of_picture: int):
    app.send_message(stadium_id, "1️⃣")
    time.sleep(1)
    app.send_message(stadium_id, "2️⃣")
    time.sleep(1)
    app.send_message(stadium_id, "3️⃣")
    time.sleep(1)

    return app.send_photo(
            stadium_id,
            match.match_images[number_of_picture].image_url,
        )


def schedule_referee(match: MatchModel, stadium_id: str, home_team: dict, away_team: dict):

    os.environ["memory"] = json.dumps(temp_memory)
    
    app.start()
    # Send scoreboard
    headers = {'Authorization': f'Token {api_token}'}
    referee = json.loads(requests.get(f'{api_url}/users/{match.referee}', headers=headers).text)


    score_board_msg = app.send_message(
        stadium_id,
        message_templates.score_board_message_template.format(
            home_team["name"],
            away_team["name"],
            home_team["stadium"]["name"],
            match.starts_at,
            referee["username"]
        )
    )

    # Save the information of message to temp memory
    temp_memory["score_board_id"] = score_board_msg.id
    temp_memory["stadium_id"] = stadium_id

    time.sleep(60)

    picture_one = send_image_match(match, stadium_id, 0)

    temp_memory["picture"] = {
        "id": picture_one.id,
        "type": match.match_images[0].image_type,
        "name": match.match_images[0].image_name.decode('utf-8'),
        "number": 0
    }

    os.environ["memory"] = json.dumps(temp_memory)

    # Start time controler
    # schedular.add_job(goal_checker.goal_time_checker, "interval", seconds=1, args=(match, stadium_id))
    # schedular.start()
    

# Goal detector
@app.on_message(filters.group & filters.create(
    lambda _, __, msg : True if msg.text == json.loads(os.environ["memory"])["picture"]["name"] else False
) & filters.create(
    lambda _, __, msg : True if msg.chat.id == json.loads(os.environ["memory"])["stadium_id"] else False
))
def goal_detector(client: Client, message: Message):
    message.reply("Goallllll!")