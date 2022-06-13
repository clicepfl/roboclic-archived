import json
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from ..config import KEYS, LIMIT, OPTIONS, POLL, STATS, logger
from ..rights import clic


@clic
def poll(update, context):
    logger.info(f"Poll started by:\n{update}")
    context.user_data.update({"user": update.message.from_user.username})

    keyboard = [
        [
            InlineKeyboardButton(option, callback_data=data)
            for data, option in list(OPTIONS.items())[4 * row : 4 * (row + 1)]
        ]
        for row in range(len(OPTIONS))
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Qui l'a dit ?", reply_markup=reply_markup, quote=False)
    try:
        update.message.delete()
    except:
        logger.info(f"Could not delete message {update.message.message_id}")

    return POLL


def poll_keyboard_handler(update, context):
    query = update.callback_query
    query.answer()
    answer = query.data
    context.user_data.update({"answer": answer})
    context.user_data.update({"callback_message": query.message})
    logger.info(f"Selected {OPTIONS[answer]}")
    query.edit_message_text(text=f"Qu'est-ce qui a été dit ?")


def create_poll(update, context):
    chat_id = update.message.chat.id
    previous_message = context.user_data["callback_message"]
    try:
        context.bot.delete_message(chat_id, previous_message.message_id)
    except:
        logger.info(f"Could not delete message {previous_message.message_id}")

    answer = context.user_data["answer"]
    logger.info(f'{OPTIONS[answer]} said "{update.message.text}"')
    question = f'Qui a dit ça : "{update.message.text}"'

    try:
        update.message.delete()
    except:
        logger.info(f"Could not delete message {update.message.message_id}")

    answer_name = OPTIONS[answer]
    options = list(OPTIONS.values())
    if len(OPTIONS) > LIMIT:
        options.remove(answer_name)
        choices = random.sample(options, LIMIT - 1)
        answer_id = random.randint(0, LIMIT - 1)
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
                KEYS["admin"], f'Poll started by @{author}\nThe answer is "{target}"'
            )
        except:
            pass

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
        # cumbersome formatting
        query_user = (
            context.args[0]
            .lower()
            .replace("é", "e")
            .replace("ï", "i")
            .replace("ë", "e")
        )
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
    states={POLL: [MessageHandler(filters=Filters.text, callback=create_poll)]},
    fallbacks=[],
)
