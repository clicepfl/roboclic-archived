import json
import random

from telegram import ReplyKeyboardButton, ReplyKeyboardMarkup, Poll
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters

from ..config import KEYS, POLL_LIMIT, OPTIONS, STATS, logger
from ..rights import clic


WHO_SAID_IT, SEND_POLL = range(1)


def sanitize(text: str) -> str:
    return ("".join(text)
        .lower()
        .replace("é", "e")
        .replace("ï", "i")
        .replace("ë", "e"))


@clic
def poll(update, context):
    logger.info(f"Poll started by:\n{update}")
    context.user_data["user"] = update.message.from_user.username
    
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    if chat_id in context.bot_data:
        return ConversationHandler.END

    context.bot_data[chat_id] = user_id

    keyboard = [
        [
            ReplyKeyboardButton(option, callback_data=data)
            for data, option in list(OPTIONS.items())[4 * row : 4 * (row + 1)]
        ]
        for row in range(len(OPTIONS))
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Qui l'a dit ?", reply_markup=reply_markup)
    try:
        update.message.delete()
    except:
        logger.info(f"Could not delete message {update.message.message_id}")

    return WHO_SAID_IT


def who_said_it(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    if user_id != context.bot_data[chat_id]:
        return WHO_SAID_IT

    answer = sanitize(update.message.text)

    if answer not in OPTIONS:
        return ConversationHandler.END

    context.user_data["answer"] = answer

    try:
        update.message.delete()
    except:
        logger.info(f"Could not delete message {update.message_id}")

    answer = context.user_data["answer"]
    logger.info(f"{OPTIONS[answer]} said \"{update.message.text}\"")
    question = f"Qui a dit ça : \"{update.message.text}\""

    try:
        update.message.delete()
    except:
        logger.info(f"Could not delete message {update.message.message_id}")

    answer_name = OPTIONS[answer]
    options = list(OPTIONS.values())
    if len(OPTIONS) > POLL_LIMIT:
        options.remove(answer_name)
        choices = random.sample(options, POLL_LIMIT - 1)
        answer_id = random.randint(0, POLL_LIMIT - 1)
        choices.insert(answer_id, answer_name)
    else:
        choices = OPTIONS.values()[:]
        random.shuffle(choices)
        answer_id = choices.index(answer_name)

    context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=choices,
        type=Poll.QUIZ,
        correct_option_id=answer_id,
        is_anonymous=False,
        allows_multiple_answers=False,
    )

    if "groups" not in KEYS or chat_id in KEYS["groups"]:
        increment_stats(answer, STATS)

    if "admin" in KEYS:
        try:
            author = context.user_data["user"]
            target = OPTIONS[context.user_data["answer"]]
            context.bot.send_message(
                KEYS["admin"], f"Poll started by @{author}\nThe answer is \"{target}\""
            )
        except:
            pass

    del context.bot_data[chat_id]

    return ConversationHandler.END


@clic
def stats(update, context):
    stats = json.load(open(STATS))
    if not len(context.args):
        text = ""
        for user, score in sorted(stats.items(), key=lambda t: t[1], reverse=True):
            text += f"{OPTIONS[user]}: {score}\n"
        if not text:
            text += "No stat available"
        update.message.reply_text(text, quote=False)
    else:
        query_user = sanitize("".join(context.args))
        user = OPTIONS.get(query_user, query_user.title())
        score = stats.get(query_user, 0)
        update.message.reply_text(f"{user}: {score}", quote=False)


def increment_stats(updated_user, stats_file):
    if not updated_user in OPTIONS:
        return
    stats = json.load(open(stats_file))
    stats.update({updated_user: stats.get(updated_user, 0) + 1})
    json.dump(stats, open(stats_file, "w"))


poll_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("poll", poll)],
    states={
        WHO_SAID_IT: [MessageHandler(filters=filters.TEXT, callback=who_said_it)],
        SEND_POLL: [MessageHandler(filters=filters.TEXT, callback=create_poll)]
    },
    fallbacks=[],
)
