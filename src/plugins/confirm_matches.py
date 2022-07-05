"""This files contains the code for the confirm matches plugin"""

from http import client
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config

from src.plugins import get_matches
from plugins.schedule_matchday import matchday_scheduler

# Load static variables
owner_id = config("OWNER_ID")


@Client.on_message(filters.user(owner_id) & filters.regex("^/get_matches$") & filters.private)
def get_matches_from_website(client: Client, message: Message):
    msg = client.send_message(
        owner_id,
        "Checking for new matches..."
    )
    get_matches.check_matches_available(msg)


def send_confirm_matches(message: Message, match_day_id: str):
    """Send confirm matches message to owner"""

    message.edit(
        "📥 New mathces are available. Do you want to confirm them?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Yes, sure!", callback_data="confirm_matches:" + str(match_day_id))],
                [InlineKeyboardButton("Hell no!", callback_data="cancel_matches:" + str(match_day_id))]
            ]
        )
    )


@Client.on_callback_query(filters.regex("^cancel_matches:\d+$"))
def cancel_matches(client: Client, callback_query: CallbackQuery):

    match_day_id = int(callback_query.data.split(":")[-1])
    callback_query.edit_message_text("❌ Matches has been canceled!")
    get_matches.cancel_matches( match_day_id )


@Client.on_callback_query(filters.regex("^confirm_matches:\d+$"))
def confirm_matches(client: Client, callback_query: CallbackQuery):

    match_day_id = int(callback_query.data.split(":")[-1])
    matchday_scheduler(client, callback_query, match_day_id)
    callback_query.edit_message_text("✅ Matches has been confirmed!")