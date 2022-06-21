"""This files contains the code for the confirm matches plugin"""

from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config

# Load static variables
owner_id = config("OWNER_ID")


def send_confirm_matches(client: Client, match_day_id: str):
    """Send confirm matches message to owner"""

    client.send_message(
        owner_id,
        "New mathces are available. Do you want to confirm them?",
        reply_markup=InlineKeyboardMarkup(
            [
                InlineKeyboardButton("Yes, sure!", callback_data="confirm_matches"),
                InlineKeyboardButton("Hell no!", callback_data="cancel_matches:" + match_day_id)
            ]
        )
    )


def confirm_matches(client: Client, message: Message):
    client.send_message(
        message.chat.id,
        "Matches are confirmed!"
    )