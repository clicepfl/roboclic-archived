import random

from .. import open_utf8_r
from ..config import ARTHUR, KEYS, RAYAN


def _quote(file):
    """
    Selects random line from file
    """
    quotes = open_utf8_r(file).read().splitlines()
    return random.choice(quotes)


def _telephone_du(reuf="reuf"):
    return f"{KEYS.get('phone', '3630')} le téléphone du {reuf} !"


def noel(update, context):
    update.message.reply_text(_telephone_du("Père Noël"), quote=False)


def reuf(update, context):
    update.message.reply_text(_telephone_du(), quote=False)


def rayan(update, context):
    update.message.reply_text(_quote(RAYAN).capitalize(), quote=False)


def arthur(update, context):
    update.message.reply_text(_quote(ARTHUR), quote=False)


def hugo(update, context):
    update.message.reply_text("???", quote=False)
