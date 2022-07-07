import os
import json

from pyrogram import filters
from pyrogram.types import Message

# Goal detector filters
def goalValidator(_, __, message: Message):
    if message.text == json.loads(os.environ["memory"])["picture"]["name"]:
        return True
    return False

goal_validator = filters.create(goalValidator)

# Stadium chat confirm
stadium_confirm = filters.chat( json.loads(os.environ["memory"])["stadium_id"] )