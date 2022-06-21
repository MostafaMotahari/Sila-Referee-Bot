"""Start message handler."""

from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message

# Decorator for start message handler
@Client.on_message(filters.regex("^/start") & filters.private)
async def start_message(client: Client, message: Message):
    """Start message handler."""

    await message.reply_text(
        "Hello, I'm SilaBot!\n"
        "I'm a bot that helps you to manage your matches.\n"
        "You can use /help to see all commands."
    )