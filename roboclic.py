from robot.config import *
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
    dp.add_handler(poll_conv_handler)
    dp.add_handler(CallbackQueryHandler(poll_keyboard_handler))
    dp.add_error_handler(error)

    # Regular handlers
    dp.add_handler(CommandHandler("help", help, pass_args=True))
    dp.add_handler(CommandHandler("cafe", coffee))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("bureau", desk))
    dp.add_handler(CommandHandler("jul", jul))
    dp.add_handler(CommandHandler("rayan", rayan))
    dp.add_handler(CommandHandler("arthur", arthur))
    dp.add_handler(CommandHandler("hugo", hugo))
    dp.add_handler(CommandHandler("bureau", desk))
    dp.add_handler(CommandHandler("soup", soup))
    dp.add_handler(CommandHandler("year", year))

    # Start the bot
    updater.start_polling()
    updater.idle()
