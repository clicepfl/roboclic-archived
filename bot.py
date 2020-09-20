import logging
import random
import unidecode

import telegram
from telegram.ext import Updater, CommandHandler


with open('api.key', 'r') as key:
    TOKEN = key.readline().strip()
    print(TOKEN)

COMMITEE = {
             'rayan': "Rayan",
             'camille': "Camille",
             'eloise': "Éloïse",
             'maelys': "Maelys",
             'hugo': "Hugo",
             'arthur': "Arthur",
             'manon': "Manon",
             'kevin': "Kévin",
             'gonxhe': "Gonxhe",
             'mallo': "Mallo",
             'tom': "Tom",
             'marine': "Marine"
            }
HOWTO = '/poll <question> <member>'
REPLY = 'Qui a dit ça : "{}"'


def start(update, context):
    update.message.reply_text(HOWTO)


def poll(update, context):

    data = update.message.text.split(' ')
    question = REPLY.format(' '.join(data[1:-1]))
    member = unidecode.unidecode(data[-1]).lower()

    if member not in COMMITEE.keys():
        update.message.replay_text(f'{member} is not in CLIC')
        return

    choices = random.sample(list(COMMITEE.values()), 10)
    answer = choices.index(COMMITEE[member])

    message = context.bot.send_poll(chat_id=update.effective_chat.id,
                                    question=question,
                                    options=choices,
                                    type=telegram.Poll.QUIZ,
                                    correct_option_id=answer,
                                    is_anonymous=False,
                                    allows_multiple_answers=False)


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
