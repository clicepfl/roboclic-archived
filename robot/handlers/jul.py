from .. import open_utf8_r
from ..config import JUL

import random
import re

from telegram import Poll


def jul(update, context):
    regex = r"\[Couplet \d : (.*?)\]"
    song = open_utf8_r(JUL).read().split("\n\n")
    choices = re.findall(regex, "$".join(song))

    block = random.choice(song)
    artist = re.search(regex, block).groups()[0]
    lyrics = block.splitlines()[1:]
    punchline = random.choice(lyrics)
    answer_id = choices.index(artist)

    question = f'Qui est l\'auteur de la punchline qui suit ?\n"{punchline}"'

    context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=choices,
        type=Poll.QUIZ,
        correct_option_id=answer_id,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
