from difflib import Match
import os
import time
import json
import requests

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from decouple import config
from apscheduler.schedulers.background import BackgroundScheduler

from src.plugins import message_templates
from src.plugins import goal_checker
from src.plugins import custom_filters
from src.sql.models import MatchModel
from src.sql.session import get_db


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
    "match_id": 0,
    "score_board_id": None,
    "picture": {
        "id": None,
        "type": None,
        "name": None,
        "number": 0
    },
    "home_team_goals": 0,
    "away_team_goals": 0
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


    wellcome_match_msg = app.send_message(
        stadium_id,
        message_templates.wellcome_match_message_template.format(
            home_team["name"],
            away_team["name"],
            home_team["stadium"]["name"],
            match.starts_at,
            referee["first_name"] + " " + referee["last_name"]
        )
    )

    score_board_msg = app.send_message(
        stadium_id,
        message_templates.score_board_message_template.format(
            home_team["name"],
            " ",
            away_team["name"],
            " "
        )
    )
    score_board_msg.pin()

    # Save the information of message to temp memory
    temp_memory["score_board_id"] = score_board_msg.id
    temp_memory["stadium_id"] = stadium_id

    time.sleep(20)

    picture_one = send_image_match(match, stadium_id, 0)

    temp_memory["picture"] = {
        "id": picture_one.id,
        "type": match.match_images[0].image_type,
        "name": match.match_images[0].image_name.decode('utf-8'),
        "number": 0
    }

    temp_memory["home_team"] = home_team
    temp_memory["away_team"] = away_team
    temp_memory["match_id"] = match.id

    os.environ["memory"] = json.dumps(temp_memory)

    # Start time controler
    # schedular.add_job(goal_checker.goal_time_checker, "interval", seconds=1, args=(match, stadium_id))
    # schedular.start()
    

# Goal detector
@app.on_message(custom_filters.goal_validator & custom_filters.stadium_confirm)
def goal_detector(client: Client, message: Message):
    db_session = get_db().__next__()
    temp_memory = json.loads(os.environ["memory"])
    match: MatchModel = db_session.query(MatchModel).filter(MatchModel.id == temp_memory["match_id"]).first()

    # Detect the scorer
    for player in temp_memory["home_team"]["players"]:
        if message.from_user.username in player.values():
            temp_memory["home_team_goals"] += 1
            break

    else:
        temp_memory["away_team_goals"] += 1

    # Send goal message
    message.reply(
        "🥸 He scored a Fucking **GOAL**",
        reply_to_message_id=message.id
    )

    # Edit the scoreboard
    scoreboard = client.get_messages(temp_memory["stadium_id"], temp_memory["score_board_id"])
    scoreboard.edit(
        message_templates.score_board_message_template.format(
            temp_memory["home_team"]["name"],
            "⚽️" * temp_memory["home_team_goals"],
            temp_memory["away_team"]["name"],
            "⚽️" * temp_memory["away_team_goals"]
        )
    )

    # Send next image confirm message
    if temp_memory["picture"]["number"] + 1 <= len(match.match_images):
        app.send_message(
            message.chat.id,
            "📲 Next picture type: **{}**\n\n\nLet's go!".format(
                match.match_images[temp_memory["picture"]["number"] + 1].image_type # upper case this
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧨 Next picture 🧨", callback_data="next_picture:")]
            ])
        )

        # Update the data of memory


    else:
        app.send_message(
            message.chat.id,
            "Match Ends!"
        )

# Next picture sender
@app.on_callback_query(filters.regex("^next_picture:"))
def send_next_picture(client: Client, callback_query: CallbackQuery):
    pass