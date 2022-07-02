"""This files contains the code for the confirm matches plugin"""

from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config

from src.plugins import get_matches

# Load static variables
owner_id = config("OWNER_ID")


def send_confirm_matches(client: Client, match_day_id: str):
    """Send confirm matches message to owner"""

    client.send_message(
        owner_id,
        "New mathces are available. Do you want to confirm them?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Yes, sure!", callback_data="confirm_matches:confirmed")],
                [InlineKeyboardButton("Hell no!", callback_data="cancel_matches:" + str(match_day_id))]
            ]
        )
    )


@Client.on_callback_query(filters.regex("^confirm_matches:confirmed$"))
def confirm_matches(client: Client, callback_query: CallbackQuery):

    callback_query.edit_message_text("Matches has been confirmed!")


@Client.on_callback_query(filters.regex("^cancel_matches:\d+$"))
def confirm_matches(client: Client, callback_query: CallbackQuery):

    callback_query.edit_message_text("Matches has been canceled!")
    get_matches.cancel_matches( int(callback_query.data.split(":")[-1]) )