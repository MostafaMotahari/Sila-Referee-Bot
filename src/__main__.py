from pyrogram.client import Client
from configparser import ConfigParser

# Load details from config file with configparser
config = ConfigParser()
config.read('src/config.ini')

TOKEN = config['ACCOUNT']['TOKEN']
API_ID = config['ACCOUNT']['API_ID']
API_HASH = config['ACCOUNT']['API_HASH']
PLUGINS = dict(root='src/plugins')

app = Client(
    "SilaBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    plugins=PLUGINS
)

if __name__ == "__main__":
    app.run()