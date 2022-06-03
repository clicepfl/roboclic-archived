from .. import open_utf8_r
from ..config import KEYS, RAYAN, ARTHUR

import random


def quote(file):
    """
    Selects random line from file
    """
    quotes = open_utf8_r(file).read().splitlines()
    return random.choice(quotes)


def telephone_du(reuf="reuf"):
    return f"{KEYS.get('phone', '3630')} le téléphone du {reuf} !"


def noel(update, context):
    update.message.reply_text(telephone_du("Père Noël"), quote=False)


def reuf(update, context):
    update.message.reply_text(telephone_du(), quote=False)


def rayan(update, context):
    update.message.reply_text(quote(RAYAN).capitalize(), quote=False)


def arthur(update, context):
    update.message.reply_text(quote(ARTHUR), quote=False)


def hugo(update, context):
    update.message.reply_text("???", quote=False)