from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
from src.plugins.get_matches import check_matches_available

@Client.on_message(filters.regex("^/get_m") & filters.private)
def get_matches(client: Client, message: Message):
    msg = message.reply_text("Checking for new matches...")
    check_matches_available(client)