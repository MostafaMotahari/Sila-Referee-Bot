import os
import time
import json
import requests

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
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
        "number": -1,
        "max_time": 30
    },
    "home_team_goals": 0,
    "away_team_goals": 0,
    "scorers": []
}

schedular = BackgroundScheduler()

UN_DUPLICATED_GOAL = False
UN_DUPLICATED_CQ = False

# app.start()

# Check Un Duplicated Goal Filter
def un_duplicated_goal(_, __, message):
    if not UN_DUPLICATED_GOAL:
        return True
    return False

# Check Un Duplicated CQ Filter
def un_duplicated_callback_query(_, __, message):
    if not UN_DUPLICATED_CQ:
        return True
    return False

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

# This func plays main role of refereeing the match
def schedule_referee(match_id, stadium_id: str, home_team: dict, away_team: dict, referee: dict):

    os.environ["memory"] = json.dumps(temp_memory)
    db_session = get_db().__next__()
    match: MatchModel = db_session.query(MatchModel).filter(MatchModel.id == match_id).first()
    try:
        app.start()
    except:
        pass
    # Send scoreboard

    app.send_photo(
        stadium_id,
        "src/static/start_match_pic.jpeg",
        caption=message_templates.wellcome_match_message_template.format(
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
            " ",
            " "
        )
    )
    score_board_msg.pin()

    # picture_one = send_image_match(match, stadium_id, 0)

    goal_detector(stadium_id=stadium_id, first_run=True)

    # Save the information of message to temp memory
    temp_memory["score_board_id"] = score_board_msg.id
    temp_memory["stadium_id"] = stadium_id

    temp_memory["home_team"] = home_team
    temp_memory["away_team"] = away_team
    temp_memory["match_id"] = match.id

    os.environ["memory"] = json.dumps(temp_memory)

    # Add handlers
    app.add_handler( MessageHandler(goal_detector, custom_filters.goal_validator & filters.create(un_duplicated_goal) & custom_filters.stadium_confirm & ~custom_filters.referee_filter(referee["user_telegram_id"])) )
    app.add_handler( CallbackQueryHandler(send_next_picture, filters.regex("^next_picture$") & filters.create(un_duplicated_callback_query) & custom_filters.referee_filter(referee["user_telegram_id"])) )



# Goal detector
def goal_detector(client: Client = None, message: Message = None, stadium_id = None, first_run: bool = False):

    # Disable goal decorator
    global UN_DUPLICATED_GOAL
    UN_DUPLICATED_GOAL = True
    global UN_DUPLICATED_CQ
    UN_DUPLICATED_CQ = False
    chat_id = stadium_id
    temp_memory = json.loads(os.environ["memory"])
    temp_memory["picture"]["name"] = "khar0k0n8y"
    os.environ["memory"] = json.dumps(temp_memory)

    # This section will run during the game
    if client:
        chat_id = message.chat.id

        # Detect the scorer
        for player in temp_memory["home_team"]["players"]:
            if message.from_user.username in player.values():
                temp_memory["home_team_goals"] += 1
                break

        else:
            temp_memory["away_team_goals"] += 1

        # Send goal congract message
        message.reply(
            "🥸 He scored a Fucking **GOAL**",
            reply_to_message_id=message.id
        )

        # Save scorer
        temp_memory["scorers"].append(f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})")

        # Edit the scoreboard
        scoreboard = client.get_messages(temp_memory["stadium_id"], temp_memory["score_board_id"])
        scoreboard.edit(
            message_templates.score_board_message_template.format(
                temp_memory["home_team"]["name"],
                "⚽️" * temp_memory["home_team_goals"],
                temp_memory["away_team"]["name"],
                "⚽️" * temp_memory["away_team_goals"],
                "\n".join(temp_memory["scorers"])
            )
        )

    # Get data from db
    db_session = get_db().__next__()
    match: MatchModel = db_session.query(MatchModel).filter(MatchModel.id == temp_memory["match_id"]).first()
    next_picture_number = temp_memory["picture"]["number"] + 1


    if not first_run:
        # Stop the timer
        schedular.remove_job("picture_timer")

        # Send next image confirm message
        if next_picture_number < len(match.match_images):
            temp_memory["picture"]["max_time"] = 30 if match.match_images[next_picture_number].image_type == "speed" else 45 if match.match_images[next_picture_number].image_type == "info" else 60
            app.send_message(
                chat_id,
                "📲 Next picture type: **{}**\n\n\nLet's go!".format(
                    match.match_images[next_picture_number].image_type.upper() # upper case this
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🧨 Next picture 🧨", callback_data="next_picture")] # Place match id in callback data later for async mode
                ])
            )

        else:
            app.send_photo(
                chat_id,
                "src/static/end_match_pic.jpeg",
                caption="Match Ends!"
            )
            # app.stop()

    else:
        app.send_message(
                chat_id,
                "📲 Fisrt picture type: **{}**\n\n\nLet's go!".format("SPEED"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🧨 Start The Match! 🧨", callback_data="next_picture")] # Place match id in callback data later for async mode
                ])
            )


    # Update data in memory
    os.environ["memory"] = json.dumps(temp_memory)


# Next picture sender
def send_next_picture(client: Client, callback_query: CallbackQuery):

    global UN_DUPLICATED_GOAL
    UN_DUPLICATED_GOAL = False
    global UN_DUPLICATED_CQ
    UN_DUPLICATED_CQ = True
    db_session = get_db().__next__()
    temp_memory = json.loads(os.environ["memory"])

    # Get match id from callback data later. for async mode
    match: MatchModel = db_session.query(MatchModel).filter(MatchModel.id == temp_memory["match_id"]).first()
    next_picture_number = temp_memory["picture"]["number"] + 1
    next_image_type = match.match_images[next_picture_number].image_type

    sent_pic = send_image_match(
        match,
        temp_memory["stadium_id"],
        next_picture_number
    )

    # Update the data of memory
    temp_memory["picture"] = {
        "id": sent_pic.id,
        "type": next_image_type,
        "name": match.match_images[next_picture_number].image_name,
        "number": next_picture_number,
        "max_time": 30 if next_image_type == "speed" else 45 if next_image_type == "info" else 60
    }

    os.environ["memory"] = json.dumps(temp_memory)

    schedular.add_job(goal_checker.goal_time_checker, "interval", seconds=1, args=(callback_query.message.chat.id, ), id="picture_timer")
    schedular.start()