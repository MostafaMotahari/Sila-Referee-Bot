import os
import time
import json

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from decouple import config

from src.plugins import message_templates
from src.sql.models import MatchModel


# Seprate session for scheduled tasks

app = Client(
    "SilaScheduleBot",
    api_id=config("API_ID"),
    api_hash=config("API_HASH"),
    bot_token=config("BOT_TOKEN"),
)

temp_memory = {
    "score_board_id": None,
}


def schedule_referee(match: MatchModel, stadium_id: str):

    # Send picture function
    def send_image_match(number_of_picture: int):
        app.send_message(stadium_id, "1️⃣")
        time.sleep(1)
        app.send_message(stadium_id, "2️⃣")
        time.sleep(1)
        app.send_message(stadium_id, "3️⃣")
        time.sleep(1)

        return app.send_photo(
                stadium_id,
                match.match_images[0].image_url,
            )


    score_board_msg = app.send_message(
        stadium_id,
        message_templates.score_board_message_template
    )

    temp_memory["score_board_id"] = score_board_msg.message_id
    temp_memory["stadium_id"] = stadium_id

    time.sleep(60)

    # picture_one = wget.download(url=match.match_images[0].image_url, out=config("DOWNLOAD_DIR"))
    

    picture_one = send_image_match(0)

    temp_memory["picture"] = {
        "id": picture_one.message_id,
        "type": match.match_images[0].image_type,
        "name": match.match_images[0].image_name,
        "number": 0
    }

    os.environ["memory"] = json.dumps(temp_memory)

    # Start time controler
    max_time = 30

    for i in max_time:
        time.sleep(1)
        secondary_temp_memory = json.loads(os.environ["memory"])

        if temp_memory["picture"]["id"] == secondary_temp_memory["picture"]["id"]:
            if max_time == 0:
                # Set things about the nex picture
                next_image_number = temp_memory["picture"]["number"] + 1
                next_image_type = match.match_images[ temp_memory["picture"]["number"] + 1 ].image_type

                # Send the next picture
                sent_pic = send_image_match(next_image_number)

                # Save the picture in memory
                temp_memory["picture"] = {
                    "id": sent_pic.message_id,
                    "type": match.match_images[next_image_number].image_type,
                    "name": match.match_images[next_image_number].image_name,
                    "number": next_image_number
                }

                os.environ["memory"] = json.dumps(temp_memory)

                # Set max time for the next picture
                max_time = 30 if next_image_type == "speed" else 45 if next_image_type == "info" else 60

            else:
                max_time -= 1


# Goal detector
@app.on_message(filters.group & filters.create(
    lambda _, __, msg : True if msg.text == json.loads(os.environ["memory"])["picture"]["name"] else False
) & filters.create(
    lambda _, __, msg : True if msg.chat.id == json.loads(os.environ["memory"])["stadium_id"] else False
))
def goal_detector(client: Client, message: Message):
    message.reply("Goallllll!")