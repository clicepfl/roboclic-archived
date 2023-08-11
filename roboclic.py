import telegram
from telegram.ext import CallbackQueryHandler, CommandHandler, Updater

from robot.config import KEYS, NORMAL_COMMANDS, logger
from robot.handlers import *
from robot.handlers.carte import CARTE_CONV_HANDLER

if __name__ == "__main__":

    def error(update, context):
        """
        Error handler
        """
        logger.warning(f'Update "{update}" caused error "{context.error}"')

    updater = Updater(token=KEYS["token"], use_context=True)
    dp = updater.dispatcher

    # Special handlers
    dp.add_handler(CommandHandler("help", help, pass_args=True))
    dp.add_handler(poll_conv_handler)
    dp.add_handler(CallbackQueryHandler(poll_keyboard_handler))
    dp.add_error_handler(error)

    updater.bot.set_chat_menu_button(None, telegram.MenuButtonCommands())
    updater.bot.set_my_commands(
        [
            telegram.BotCommand("arthur", "Ressort une citation d'Arthur"),
            telegram.BotCommand("birthday", "Crée une devinette de date d'anniversaire"),
            telegram.BotCommand("bureau", "Crée un sondage pour savoir qui est au/près du bureau"),
            telegram.BotCommand("cafe", "Indique la quantité de café au bureau"),
            telegram.BotCommand("carte", "Indique/modifie qui est en possession de la carte invité"),
            telegram.BotCommand("countdown", "Fait probablement quelquechose"),
            telegram.BotCommand("help", "Voir /help"),
            telegram.BotCommand("hugo", "Ressort une citation de Hugo"),
            telegram.BotCommand("jul", "Crée une devinette sur des rappeurs"),
            telegram.BotCommand("noel", "Donne le tel du Père Noël"),
            telegram.BotCommand("poll", "Permet de créer un quiz sur une quote d'un comité"),
            telegram.BotCommand("rayan", "Ressort une citation de Rayan"),
            telegram.BotCommand("reuf", "Donne le tel du reuf"),
            telegram.BotCommand("soup", "Technical difficulties, please stand by"),
            telegram.BotCommand("year", "Indique l'avancement dans l'année"),
        ]
    )

    # Regular handlers
    try:
        for fname in NORMAL_COMMANDS:
            dp.add_handler(CommandHandler(fname, globals()[fname]))
    except KeyError:
        logger.info(f"{fname} handler not found/imported")

    # Carte
    dp.add_handler(CARTE_CONV_HANDLER)

    # Start the bot
    updater.start_polling()
    updater.idle()
