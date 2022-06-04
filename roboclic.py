from setuptools import Command
from robot.config import KEYS, NORMAL_COMMANDS, logger
from robot.handlers import *

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
)


if __name__ == "__main__":

    def error(update, context):
        """
        Error handler
        """
        logger.warning(f'Update "{update}" caused error "{context.error}"')

    logger.info(f"Keys: {KEYS}")

    updater = Updater(token=KEYS["token"], use_context=True)
    dp = updater.dispatcher

    # Special handlers
    dp.add_handler(CommandHandler("help", help, pass_args=True))
    dp.add_handler(poll_conv_handler)
    dp.add_handler(CallbackQueryHandler(poll_keyboard_handler))
    dp.add_error_handler(error)

    # Regular handlers
    try:
        for fname in NORMAL_COMMANDS:
            dp.add_handler(CommandHandler(fname, globals()[fname]))
    except KeyError:
        logger.info(f"{fname} handler not found/imported")

    # Start the bot
    updater.start_polling()
    updater.idle()
