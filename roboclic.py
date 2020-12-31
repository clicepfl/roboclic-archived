import logging
import random
import json
import re
import pytz
from datetime import datetime

from telegram import Poll, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler


LIMIT = 10
POLL = 0
JUL = 'jul.txt'
RAYAN = 'rayan.txt'
ARTHUR = 'arthur.txt'

KEYS = dict(line.strip().split('=') for line in open('.keys'))
OPTIONS = json.loads(open('options.json').read())
BIRTHDAYS = json.loads(open('birthday.json').read())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def quote(file):
    quotes = open(file, 'r').read().splitlines()
    return random.choice(quotes)


def rayan(update, context):
    update.message.reply_text(quote(RAYAN).capitalize(), quote=False)


def arthur(update, context):
    update.message.reply_text(quote(ARTHUR), quote=False)


def countdown(*time):
    r = datetime(*time) - datetime.now()
    return r.days, r.seconds // 3600, r.seconds % 3600 // 60


def qalf(update, context):
    w = countdown(2021, 4, 26)
    update.message.reply_text('{}j {}h {}m'.format(*w), quote=False)


def kaamelott(update, context):
    update.message.reply_text("Film reporté à 2021")
    #w = countdown(2021, 11, 25)
    #update.message.reply_text('{}j {}h {}m'.format(*w), quote=False)


def get_time(timedelta):
    return timedelta.days * 24 * 60 * 60 + timedelta.seconds


def year(update, contact):
    timezone = pytz.timezone('Europe/Zurich')
    today = datetime.now(timezone)
    start = datetime(today.year, 1, 1, 0, 0).astimezone(timezone)
    end = datetime(today.year, 12, 31, 23, 59).astimezone(timezone)

    passed = today - start
    total = end - start

    percent = max(0, get_time(passed) / get_time(total) * 100)
    display = progression_bar(percent)

    update.message.reply_text('{:.2f}%\n{}'.format(percent, display), quote=False)


def progression_bar(percent):
    total = 25
    tiles = min(total, int(round(percent / 4)))
    return '[' + '#' * tiles + '-' * (total - tiles) + ']'


def oss(update, context):
    w = countdown(2021, 2, 3)
    update.message.reply_text('{}j {}h {}m'.format(*w), quote=False)


def jul(update, context):
    regex = r'\[Couplet \d : (.*?)\]'
    song = open(JUL, 'r').read().split('\n\n')
    choices = re.findall(regex, '$'.join(song))

    block = random.choice(song)
    artist = re.search(regex, block).groups()[0]
    lyrics = block.splitlines()[1:]
    punchline = random.choice(lyrics)
    answer_id = choices.index(artist)

    question = f"Qui est l'auteur de la punchline qui suit ?\n\"{punchline}\""

    context.bot.send_poll(chat_id=update.effective_chat.id,
                          question=question,
                          options=choices,
                          type=Poll.QUIZ,
                          correct_option_id=answer_id,
                          is_anonymous=False,
                          allows_multiple_answers=False)


def poll(update, context):
    logger.info(f'Bot started by {update.message.from_user}')

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
    logger.info(f'Selected {OPTIONS[answer]}')
    query.edit_message_text(text=f"Qu'est-ce qui a été dit ?")


def create_poll(update, context):
    answer = context.user_data['answer']
    logger.info(f'{OPTIONS[answer]} said "{update.message.text}"')
    question = f'Qui a dit ça : "{update.message.text}"'

    username = OPTIONS[answer]
    options = list(OPTIONS.values())
    if len(OPTIONS) > LIMIT:
        options.remove(username)
        choices = random.sample(options, LIMIT - 1)
        answer_id = random.randint(0, LIMIT - 1)
        choices.insert(answer_id, username)
    else:
        choices = random.sample(OPTIONS.values(), LIMIT)
        answer_id = choices.index(username)

    context.bot.send_poll(chat_id=update.effective_chat.id,
                          question=question,
                          options=choices,
                          type=Poll.QUIZ,
                          correct_option_id=answer_id,
                          is_anonymous=False,
                          allows_multiple_answers=False)

    return ConversationHandler.END


def birthday(update, context):
    options = list(OPTIONS.values())
    user_id = random.sample(list(OPTIONS), 1)[0]

    username = OPTIONS[user_id]
    date = BIRTHDAYS[user_id]

    question = f"Qui est né le {date} ?"

    if len(OPTIONS) > LIMIT:
        options.remove(username)
        choices = random.sample(options, LIMIT - 1)
        answer_id = random.randint(0, LIMIT - 1)
        choices.insert(answer_id, username)
    else:
        choices = random.sample(OPTIONS.values(), LIMIT)
        answer_id = choices.index(username)

    context.bot.send_poll(chat_id=update.effective_chat.id,
                          question=question,
                          options=choices,
                          type=Poll.QUIZ,
                          correct_option_id=answer_id,
                          is_anonymous=False,
                          allows_multiple_answers=False)


def reuf(update, context):
    update.message.reply_text("+41 76 399 46 20 le téléphone du reuf !", quote=False)


def hugo(update, context):
    update.message.reply_text("???", quote=False)


def error(update, context):
    logger.warning(f'Update "{update}" caused error "{context.error}"')


def help(update, context):
    update.message.reply_text("Type /poll to use me.")


if __name__ == '__main__':
    logger.info(f'Keys: {KEYS}')
    updater = Updater(token=KEYS['token'], use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('poll', poll)],
        states={POLL: [MessageHandler(filters=Filters.text, callback=create_poll)]},
        fallbacks=[]
    )

    dp.add_handler(CommandHandler('qalf', qalf))
    dp.add_handler(CommandHandler('kaamelott', kaamelott))
    dp.add_handler(CommandHandler('oss', oss))
    dp.add_handler(CommandHandler('jul', jul))
    dp.add_handler(CommandHandler('hugo', hugo))
    dp.add_handler(CommandHandler('reuf', reuf))
    dp.add_handler(CommandHandler('arthur', arthur))
    dp.add_handler(CommandHandler('rayan', rayan))
    dp.add_handler(CommandHandler('birthday', birthday))
    dp.add_handler(CommandHandler('year', year))
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(keyboard_handler))
    dp.add_handler(CommandHandler('help', help))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
