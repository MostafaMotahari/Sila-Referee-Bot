""""This files is the main file of the bot"""

import os

from pyrogram.client import Client
from decouple import config


PLUGINS = dict(root='src/plugins')

app = Client(
    "SilaBot",
    api_id=config("API_ID"),
    api_hash=config("API_HASH"),
    bot_token=config("BOT_TOKEN"),
    plugins=PLUGINS
)

if __name__ == "__main__":
    app.run()