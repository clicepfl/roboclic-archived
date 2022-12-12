from telegram.ext import Application, CommandHandler, filters

from robot.config import KEYS, NORMAL_COMMANDS, logger
from robot.handlers import *

if __name__ == "__main__":

    def error(update, context):
        """
        Error handler
        """
        logger.warning(f"Update \"{update}\" caused error \"{context.error}\"")
    
    app = Application.builder().token(KEYS["token"]).build()

    conv_filter = filters.TEXT & (~filters.COMMAND)

    # Special handlers
    app.add_handler(CommandHandler("help", help, pass_args=True))
    app.add_handler(poll_conv_handler, 0)
    app.add_handler(carte_conv_handler, 0)
    app.add_error_handler(error)

    # Regular handlers
    try:
        for fname in NORMAL_COMMANDS:
            app.add_handler(CommandHandler(fname, globals()[fname]), 1)
    except KeyError:
        logger.info(f"{fname} handler not found/imported")

    # Start the bot
    app.run_polling()
