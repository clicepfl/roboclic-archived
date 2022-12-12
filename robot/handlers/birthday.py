import random

from telegram import Poll

from ..config import BIRTHDAYS, POLL_LIMIT, OPTIONS
from ..rights import clic


@clic
def birthday(update, context):
    options = list(OPTIONS.values())
    user_id = random.sample(list(OPTIONS), 1)[0]

    username = OPTIONS[user_id]
    date = BIRTHDAYS[user_id]

    question = f"Qui est né le {date} ?"

    if len(OPTIONS) > POLL_LIMIT:
        options.remove(username)
        choices = random.sample(options, POLL_LIMIT - 1)
        answer_id = random.randint(0, POLL_LIMIT - 1)
        choices.insert(answer_id, username)
    else:
        choices = random.sample(OPTIONS.values(), POLL_LIMIT)
        answer_id = choices.index(username)

    context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=choices,
        type=Poll.QUIZ,
        correct_option_id=answer_id,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
