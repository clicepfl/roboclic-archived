import logging
import random
import json

import unidecode
from telegram import Poll, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler


LIMIT = 10
QUESTION, POLL = range(2)

with open('api.key', 'r') as key:
    TOKEN = key.readline().strip()

with open('options.json', 'r') as options:
    OPTIONS = json.loads(options.read())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = [
                    [
                        InlineKeyboardButton(option, callback_data=data)
                        for data, option in list(OPTIONS.items())[4*row:4*(row+1)]
                    ]
                    for row in range(len(OPTIONS))
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Qui l'a dit ?", reply_markup=reply_markup, quote=False)

    return POLL


def keyboard_handler(update, context):
    query = update.callback_query
    query.answer()
    answer = query.data
    context.user_data['answer'] = answer
    query.edit_message_text(text="Qu'est-ce que {} a dit ?".format(OPTIONS[answer]))


def poll(update, context):
    question = 'Qui a dit ça : "{}"'.format(update.message.text)
    answer = context.user_data['answer']
    options = list(OPTIONS.values())
    if len(OPTIONS) > LIMIT:
        options.remove(OPTIONS[answer])
        choices = random.sample(options, LIMIT - 1)
        answer_id = random.randint(0, LIMIT - 1)
        choices.insert(answer_id, OPTIONS[answer])
    else:
        choices = random.sample(OPTIONS.values(), LIMIT)
        answer_id = choices.index(OPTIONS[answer])

    context.bot.send_poll(chat_id=update.effective_chat.id,
                          question=question,
                          options=choices,
                          type=Poll.QUIZ,
                          correct_option_id=answer_id,
                          is_anonymous=False,
                          allows_multiple_answers=False)

    return ConversationHandler.END


def help(update, context):
    update.message.reply_text("Type /start to use me. I'll deliver you a poll that you can transfer to anyone!")


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={POLL: [MessageHandler(filters=Filters.text, callback=poll)]},
        fallbacks=[]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(keyboard_handler))
    dp.add_handler(CommandHandler('help', help))
    updater.start_polling()
    updater.idle()
