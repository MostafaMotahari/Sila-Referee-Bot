import os
import json
import regex

from pyrogram import filters
from pyrogram.types import Message

# Goal detector filters
def goalValidator(_, __, message: Message):
    try:
        for part_name in json.loads(os.environ["memory"])["picture"]["name"].split(" "):
            pattern = r"(?e)(?:" + part_name + r"){e<=1}"

            if regex.fullmatch(pattern, message.text):
                return True

        else:
            return False
    except:
        return False

goal_validator = filters.create(goalValidator)

# Stadium chat confirm
def stadiumConfirm(_, __, message: Message):
    if message.chat.id == json.loads(os.environ["memory"])["stadium_id"]:
        return True
    return False

stadium_confirm = filters.create(stadiumConfirm)

# Referee filter
def referee_filter(referee_username: str):
    def ___(_, __, message: Message):
        if _.referee_username == message.from_user.username:
            return True
        return False

    return filters.create(___, referee_username=referee_username)