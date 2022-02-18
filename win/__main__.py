from telegram.ext import Updater

from . import handlers
from .config import configure_logging, settings
from .db import create_db_and_tables


def main():
    configure_logging()
    create_db_and_tables()

    updater = Updater(token=settings.TELEGRAM_API_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(handlers.start)
    dispatcher.add_handler(handlers.stats)
    dispatcher.add_handler(handlers.activity_creation_conversation)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
