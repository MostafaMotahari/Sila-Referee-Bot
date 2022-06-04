import os
from pyrogram.client import Client
from configparser import ConfigParser
from src.sql.base_class import Base
from src.sql.session import engine

# Load details from config file with configparser
config = ConfigParser()
config.read('src/config.ini')

TOKEN = config['ACCOUNT']['TOKEN']
API_ID = config['ACCOUNT']['API_ID']
API_HASH = config['ACCOUNT']['API_HASH']
API_URL = config['API']['URL']
DB_URL = config['SQL']['HOST']
PLUGINS = dict(root='src/plugins')

app = Client(
    "SilaBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    plugins=PLUGINS
)

if __name__ == "__main__":
    # Set environment variable
    os.environ['db_url'] = DB_URL
    os.environ['api_url'] = API_URL
    # Connect to data base
    Base.metadata.create_all(bind=engine)

    app.run()