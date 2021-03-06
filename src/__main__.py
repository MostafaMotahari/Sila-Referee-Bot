""""This files is the main file of the bot"""

import os, time

from pyrogram.client import Client
from decouple import config

from src.sql.session import engine
from src.sql.base_class import Base

from src.sql.methods import test


PLUGINS = dict(root='src/plugins')

app = Client(
    "SilaAPIBot",
    api_id=config("API_ID"),
    api_hash=config("API_HASH"),
    bot_token=config("BOT_TOKEN"),
    plugins=PLUGINS
)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    os.environ['TZ'] = 'Asia/Tehran'
    time.tzset()
    try:
        test()
    except:
        pass
    app.run()