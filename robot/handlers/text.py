import random

from .. import open_utf8_r
from ..config import ARTHUR, KEYS, RAYAN
from ..rights import clic


def _quote(file):
    """
    Selects random line from file
    """
    quotes = open_utf8_r(file).read().splitlines()
    return random.choice(quotes)


def _telephone_du(reuf="reuf"):
    return f"{KEYS.get('phone', '3630')} le téléphone du {reuf} !"


@clic
def noel(update, context):
    update.message.reply_text(_telephone_du("Père Noël"), quote=False)


@clic
def reuf(update, context):
    update.message.reply_text(_telephone_du(), quote=False)


@clic
def rayan(update, context):
    update.message.reply_text(_quote(RAYAN).capitalize(), quote=False)


@clic
def arthur(update, context):
    update.message.reply_text(_quote(ARTHUR), quote=False)


@clic
def hugo(update, context):
    update.message.reply_text("???", quote=False)
