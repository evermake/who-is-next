__all__ = ["start", "stats"]

from sqlmodel import select
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from win.db import get_session
from win.models import User


def handle_start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi!👋 To create an activity send me /create")

    user_id = update.effective_user.id
    statement = select(User).where(User.telegram_id == user_id)

    with get_session() as session:
        if not session.exec(statement).first():
            session.add(User(telegram_id=user_id))
            session.commit()


def handle_stats(update: Update, context: CallbackContext):
    update.message.reply_text("🛠")


start = CommandHandler("start", handle_start)
stats = CommandHandler("stats", handle_stats)
