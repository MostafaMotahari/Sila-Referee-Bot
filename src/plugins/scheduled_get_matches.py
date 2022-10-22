from pyrogram.client import Client
from pyrogram.types import Message
from decouple import config

from src.plugins.get_matches import check_matches_available

PLUGINS = dict(root='src/plugins')

app = Client(
    "SilaScheduleBot",
    api_id=config("API_ID"),
    api_hash=config("API_HASH"),
    bot_token=config("BOT_TOKEN"),
    # plugins=PLUGINS
)

def get_matches():
    app.start()
    msg = app.send_message(
        "TheAlternativeMousiol",
        "Checking for new matches..."
    )
    check_matches_available(msg)
    app.stop()
