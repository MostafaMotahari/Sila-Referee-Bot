""""This files is the main file of the bot"""

import os
from pytz import utc

from pyrogram.client import Client
from decouple import config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from src.sql.session import engine
from src.sql.base_class import Base
from src.plugins import scheduled_get_matches

# from src.sql.methods import test


PLUGINS = dict(root='src/plugins')

app = Client(
    "SilaCliBot",
    api_id=config("API_ID"),
    api_hash=config("API_HASH"),
    # bot_token=config("BOT_TOKEN"),
    # plugins=PLUGINS
)


jobstores = {
    'default': SQLAlchemyJobStore(url=config('DB_URL'))
}
executors = {
    'default': ThreadPoolExecutor(20),
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 15*60
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(scheduled_get_matches.get_matches, "interval", seconds = 30)
    scheduler.start()
    app.run()