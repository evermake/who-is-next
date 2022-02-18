__all__ = ["activity_creation_conversation"]

from enum import IntEnum
from typing import Union

from sqlmodel import select
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from win.db import get_session
from win.models import Activity, Participant
from win.utils.random_activity_name import get_random_activity_name


class ConversationState(IntEnum):
    CHOOSING_NAME = 1
    ADDING_PARTICIPANT = 2
    CONFIRMING = 3
    END = ConversationHandler.END


ADD_ME_MESSAGE = "🙋Add me"
add_me_markup = ReplyKeyboardMarkup(
    [[ADD_ME_MESSAGE]], one_time_keyboard=True, resize_keyboard=True
)

RANDOM_ACTIVITY_NAME_MESSAGE = "🎲 Random 🎲"
random_name_markup = ReplyKeyboardMarkup(
    [[RANDOM_ACTIVITY_NAME_MESSAGE]],
    one_time_keyboard=True,
    resize_keyboard=True,
)


def get_activity_preview_html(activity: Activity) -> str:
    participant_strings = []
    for participant in activity.participants:
        participant_strings.append(f" - <i>{participant.name}</i>")

    return 'Activity: <b>"%s"</b>\n\nParticipants:\n%s' % (
        activity.name,
        "\n".join(participant_strings),
    )


def validate_activity_name(name: str, chat_id: int) -> Union[str, bool]:
    if name.startswith("/"):
        return 'activity name cannot start with "/"'

    with get_session() as session:
        statement = (
            select(Activity)
            .where(Activity.chat_id == chat_id)
            .where(Activity.name == name)
        )
        if session.exec(statement).first():
            return f'activity with name "{name}"already exists in the chat'

    return True


# - - - Commands - - -


def cancel(update: Update, context: CallbackContext) -> int:
    del context.chat_data["activity"]
    update.message.reply_text("Canceled.")
    return ConversationState.END


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Let's create an activity.\nFirst, choose a name:",
        reply_markup=random_name_markup,
    )
    context.chat_data["activity"] = Activity(
        name="__undefined__", chat_id=update.message.chat_id
    )
    return ConversationState.CHOOSING_NAME


def choose_name(update: Update, context: CallbackContext) -> int:
    activity_name = update.message.text

    if activity_name == RANDOM_ACTIVITY_NAME_MESSAGE:
        activity_name = get_random_activity_name()

    validation_result = validate_activity_name(
        activity_name, update.effective_chat.id
    )

    if validation_result is not True:
        update.message.reply_text(
            f"❌ Choose another name:\n{validation_result}"
        )
        return ConversationState.CHOOSING_NAME

    context.chat_data["activity"].name = activity_name
    update.message.reply_text(
        f"Great! Who will be responsible for <b>{activity_name}</b>?",
        parse_mode=ParseMode.HTML,
        reply_markup=add_me_markup,
    )
    return ConversationState.ADDING_PARTICIPANT


def add_participant_by_message_text(
    update: Update, context: CallbackContext
) -> int:
    participant = Participant(name=update.message.text)
    return add_participant(
        update=update,
        context=context,
        participant=participant,
        already_exists_error_msg="%(name)s is already added!",
    )


def add_participant_by_sender(update: Update, context: CallbackContext) -> int:
    participant = Participant(
        name=update.effective_user.name, telegram_id=update.effective_user.id
    )
    return add_participant(
        update=update,
        context=context,
        participant=participant,
        already_exists_error_msg="%(name)s, you are already added!",
    )


def add_participant(
    update: Update,
    context: CallbackContext,
    participant: Participant,
    already_exists_error_msg: str,
    success_msg: str = "%(name)s, okay. Anyone else?",
):
    activity: Activity = context.chat_data["activity"]
    if participant in activity.participants:
        update.message.reply_text(
            already_exists_error_msg % {"name": participant.name}
        )
        return ConversationState.ADDING_PARTICIPANT

    activity.participants.append(participant)
    update.message.reply_text(success_msg % {"name": participant.name})
    return ConversationState.ADDING_PARTICIPANT


def show_preview(update: Update, context: CallbackContext):
    activity: Activity = context.chat_data["activity"]
    update.message.reply_text(
        get_activity_preview_html(activity)
        + "\n\nType /confirm to save an activity",
        parse_mode=ParseMode.HTML,
    )
    return ConversationState.CONFIRMING


def confirm(update: Update, context: CallbackContext):
    activity: Activity = context.chat_data["activity"]

    with get_session() as session:
        session.add(activity)
        session.commit()
        update.message.reply_text("✅ Activity saved.")
        return ConversationState.END


# - - - End of commands - - -


activity_creation_conversation = ConversationHandler(
    entry_points=[CommandHandler("create", start)],
    states={
        ConversationState.CHOOSING_NAME: [
            CommandHandler("cancel", cancel),
            MessageHandler(Filters.text, choose_name),
        ],
        ConversationState.ADDING_PARTICIPANT: [
            CommandHandler("preview", show_preview),
            CommandHandler("add_me", add_participant_by_sender),
            MessageHandler(
                Filters.regex(rf"^{ADD_ME_MESSAGE}$"),
                add_participant_by_sender,
            ),
            MessageHandler(
                Filters.text & (~Filters.command),
                add_participant_by_message_text,
            ),
        ],
        ConversationState.CONFIRMING: [CommandHandler("confirm", confirm)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_chat=True,
    per_user=False,
)
