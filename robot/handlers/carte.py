from ..rights import clic
from ..config import COMITE_IDS

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Filters

AU_BUREAU = "-1"
CARTE_START, CARTE_GIVE = range(2)


@clic
def carte_start(update, context) -> None:
    if "carte" not in context.bot_data:
        context.bot_data["carte"] = {"current": AU_BUREAU, "last": AU_BUREAU, "message": -1}

    current = context.bot_data["carte"]["current"]
    last = context.bot_data["carte"]["last"]

    if current == "-1":
        text = f"🃏 La carte est actuellement au bureau"
        if current != last:
            text += f" (récupérée par {last})"
        text += "."
        keyboard = [
            [
                InlineKeyboardButton("Prendre", callback_data="take"),
                InlineKeyboardButton("Donner", callback_data="give"),
            ],
        ]
    else:
        text = f"🃏 La carte est actuellement chez {current}"
        if current != last:
            text += f" (donnée par {last})"
        text += "."
        keyboard = [
            [
                InlineKeyboardButton("Retour bureau", callback_data="home"),
                InlineKeyboardButton("Transmettre", callback_data="give"),
            ],
        ]

    keyboard.append([InlineKeyboardButton("Just checking, merci !", callback_data="cancel")])

    if COMITE_IDS:
        reply_markup = InlineKeyboardMarkup(keyboard) if update.message.from_user.id in COMITE_IDS else None
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)

    m = update.message.reply_text(text, reply_markup=reply_markup)
    context.bot_data["carte"]["message"] = m.message_id

    return CARTE_START


def carte_choices(update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query_name = query.from_user.first_name
    if COMITE_IDS and query.from_user.id not in COMITE_IDS:
        return

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    if query.data == "cancel":
        query.edit_message_text(text="A bientôt !")

        return ConversationHandler.END
    elif query.data == "give":
        context.bot_data["carte"]["last"] = query_name
        keyboard = [[InlineKeyboardButton("Annuler", callback_data="cancel")]]

        query.edit_message_text(text="🃏 A qui donner la carte ?\n(Tu peux répondre directement)", reply_markup=InlineKeyboardMarkup(keyboard))

        return CARTE_GIVE
    else:
        last = context.bot_data["carte"]["last"] = query_name

        if query.data == "home":
            context.bot_data["carte"]["current"] = AU_BUREAU
            text = f"🃏 La carte est de retour au bureau (récupérée par {last})."
        elif query.data == "take":
            current = context.bot_data["carte"]["current"] = query_name
            text = f"🃏 La carte a été prise par {current}."
        else:
            text = "🃏 ???"

        query.edit_message_text(text=text)

        return ConversationHandler.END


def carte_give(update, context) -> None:
    current = context.bot_data["carte"]["current"] = update.message.text
    last = context.bot_data["carte"]["last"]
    m_id = context.bot_data["carte"]["message"]
    c_id = update.message.chat.id

    context.bot.edit_message_text(f"🃏 La carte a été donnée à {current} par {last}.", chat_id=c_id, message_id=m_id)

    return ConversationHandler.END


CARTE_CONV_HANDLER = ConversationHandler(
        entry_points=[CommandHandler("carte", carte_start)],
        states={
            CARTE_START: [
                CallbackQueryHandler(carte_choices, pattern="^take$"),
                CallbackQueryHandler(carte_choices, pattern="^give$"),
                CallbackQueryHandler(carte_choices, pattern="^home$"),
                CallbackQueryHandler(carte_choices, pattern="^cancel"),
            ],
            CARTE_GIVE: [
                MessageHandler(Filters.text & ~Filters.command, carte_give),
                CallbackQueryHandler(carte_choices, pattern="^cancel"),
            ],
        },
        fallbacks=[CommandHandler("carte", carte_start)],
    )
