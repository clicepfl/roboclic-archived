import logging
import random
import json

import unidecode
import telegram
from telegram.ext import Updater, CommandHandler


HOWTO = '/poll question member'
REPLY = 'Qui a dit ça : "{}"'
LIMIT = 10

with open('api.key', 'r') as key:
    TOKEN = key.readline().strip()
    print(TOKEN)

with open('options.json', 'r') as options:
    OPTIONS = json.loads(options.read())


def start(update, context):
    update.message.reply_text(HOWTO)


def poll(update, context):

    data = update.message.text.split(' ')

    if len(data) < 3:
        update.message.reply_text('Wrong format, type /help for more info')
        return

    question = REPLY.format(' '.join(data[1:-1]))
    answer = unidecode.unidecode(data[-1]).lower()

    if answer not in OPTIONS.keys():
        update.message.reply_text(f'{data[-1]} is not in CLIC')
        return

    display_options = list(OPTIONS.values())

    if len(OPTIONS) > LIMIT:
        display_options.remove(OPTIONS[answer])
        choices = random.sample(display_options, LIMIT - 1)
        answer_id = random.randint(0, LIMIT - 1)
        choices.insert(answer_id, OPTIONS[answer])
    else:
        choices = random.sample(display_options, LIMIT)
        answer_id = choices.index(OPTIONS[answer])

    context.bot.send_poll(chat_id=update.effective_chat.id,
                          question=question,
                          options=choices,
                          type=telegram.Poll.QUIZ,
                          correct_option_id=answer_id,
                          is_anonymous=False,
                          allows_multiple_answers=False)


# TODO: write a cleaner help message
def help_handler(update, context):
    update.message.reply_text(HOWTO)


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('poll', poll))
    dp.add_handler(CommandHandler('help', help_handler))

    updater.start_polling()
    updater.idle()
